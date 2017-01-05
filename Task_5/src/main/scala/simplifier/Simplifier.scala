package simplifier

import AST._
import scala.language.postfixOps
// to implement
// avoid one huge match of cases
// take into account non-greedy strategies to resolve cases with power laws
object Simplifier {

  type Simplify[T] = PartialFunction[T, Node]

  val simplify:Simplify[Node] = {
    case NodeList(l) => simplifyNodeList(l map simplify)
    case BinExpr(op, l, r) => simplifyBinExpr(op, simplify(l), simplify(r))
    case Unary(op, v) => simplifyUnExpr(op, simplify(v))
    case ConditionalInstr(l, d) =>
      simplifyConditionalInstr((l map {
        case ConditionSuitePair(bt, c, s) => ConditionSuitePair(bt, simplify(c), simplify(s))
      }, d map simplify))
    case IfElseExpr(cond, l, r) => simplifyIfElseExpr(simplify(cond), simplify(l), simplify(r))
    case Assignment(l, r) => simplifyAssignment(simplify(l), simplify(r))
    case WhileInstr(cond, body) => simplifyWhileInstr(simplify(cond), simplify(body))
    case n:Node => n
  }

  lazy val simplifyAssignment:Simplify[(Node, Node)] = {
    case (l, r) if l == r => NodeList()
    case (l, r) => Assignment(l, r)
  }

  def simplifyNodeList(list: List[Node]):Node = {
    removeDeadAssignments(list filterNot (_==NodeList())) match {
      case n :: Nil => n
      case l => l
    }
  }

  def removeDeadAssignments(l: List[Node]):List[Node] = l match {
    case (a1:Assignment) :: (a2:Assignment) :: rest if a1.left == a2.left
      => removeDeadAssignments(a2 :: rest)
    case n :: rest => n :: removeDeadAssignments(rest)
    case Nil => Nil
  }

  lazy val simplifyWhileInstr:Simplify[(Node, Node)] = {
    case (FalseConst, _) => NodeList()
    case (cond, body) => WhileInstr(cond, body)
  }

  lazy val simplifyConditionalInstr:Simplify[(List[ConditionSuitePair], Option[Node])] = {
    case (l, d) if l exists (_.condition == TrueConst) => l.find(_.condition == TrueConst).get.suite
    case (l, d) if l forall (_.condition == FalseConst) => d getOrElse NodeList()
    case (l, d) => ConditionalInstr(l, d)
  }

  lazy val simplifyIfElseExpr:Simplify[(Node, Node, Node)] = {
    case (TrueConst, l, r) => l
    case (FalseConst, l, r) => r
    case (cond, l, r) => IfElseExpr(cond, l, r)
  }

  type BinExprTuple = (String, Node, Node)
  lazy val simplifyBinExprWithoutRecovery = simplifyBinExprLogic
  lazy val simplifyBinExpr = simplifyBinExprLogic orElse simplifyBinExprRecovery

  lazy val simplifyBinExprLogic:Simplify[BinExprTuple] = {
    //concat tuples
    case ("+", Tuple(l1), Tuple(l2)) => Tuple(l1 ++ l2)

    //concat lists
    case ("+", ElemList(l1), ElemList(l2)) => ElemList(l1 ++ l2)

    //recognize power laws
    case ("*", BinExpr("**", a, b), BinExpr("**", c, d)) if a == c => simplifyBinExpr("**", a, simplifyBinExpr("+", b, d))
    case ("**", BinExpr("**", a, b), c) => simplifyBinExpr("**", a, simplifyBinExpr("*", b, c))
    case ("**", a, IntNum(0)) => 1
    case ("**", a, IntNum(1)) => a
    case ("+",
      BinExpr(op@("+"|"-"),
      BinExpr("**", a,IntNum(2)),BinExpr("*",BinExpr("*",IntNum(2),b),c)),BinExpr("**",d,IntNum(2)))
      if a == b && c == d =>
        simplifyBinExpr("**", simplifyBinExpr(op, a, c), 2)
    case ("-",
      BinExpr("-", BinExpr("**",BinExpr("+",a,b),IntNum(2)),BinExpr("**",a1,IntNum(2))),
      BinExpr("*",BinExpr("*",IntNum(2),a2),b1))
      if a == a1 && a1 == a2 && b == b1
      => simplifyBinExpr("**", b, 2)
    case ("-",BinExpr("**",BinExpr("+",a,b),IntNum(2)),BinExpr("**",BinExpr("-",a1,b1),IntNum(2)))
      if a == a1 && b == b1
      => simplifyBinExpr("*", simplifyBinExpr("*", 4, a), b)

    //eval known exprs
    case (op, IntNum(a), IntNum(b)) => evalBinExpr(op, a, b).toInt
    case (op, Num(a), Num(b)) => evalBinExpr(op, a, b)

    //understand distributive property of multiplication
    case (op@("+"|"-"), BinExpr("*", a, b), BinExpr("*", c, d)) if Set(a, b) intersect Set(c, d) nonEmpty
      =>
        val (x, y) = (Set(a, b), Set(c, d))
        simplifyBinExpr("*", x & y last, simplifyBinExpr(op, x -- (x & y) last, y -- (x & y) last))
    case (op@("+"|"-"), a, o@BinExpr("*", b, c)) if a == b || a == c
      => simplifyBinExpr(op, BinExpr("*", a, 1), o)

    //simplify easy exprs
    //case (op, IntNum(0), x) if "+" :: "and" :: Nil contains op => x
  }

  lazy val simplifyBinExprRecovery:Simplify[BinExprTuple] = {
    case (op, l, r) if !(simplifyBinExprWithoutRecovery isDefinedAt (op, r, l)) =>
      BinExpr(op, l, r)
    case (op@("+" | "and" | "*" | "or"), l, r) => simplifyBinExprWithoutRecovery(op, r, l)
    case (op@("-"), l, r) => simplifyUnExpr(op, simplifyBinExprWithoutRecovery(op, r, l))
    case (op, l, r) => BinExpr(op, l, r)
  }


  lazy val evalBinExpr = PartialFunction[(String, Double, Double), Double] {
    case ("**", a, b) => math.pow(a, b)
    case ("+", a, b) => a + b
    case ("-", a, b) => a - b
    case ("*", a, b) => a * b
    case ("/", a, b) => a / b
  }

  lazy val simplifyUnExpr:Simplify[(String, Node)] = {
    case ("not", TrueConst) => FalseConst
    case ("not", FalseConst) => TrueConst
    case ("not" | "-", Unary("not" | "-", v)) => v
    case (op, v) => Unary(op, v)
  }

}
