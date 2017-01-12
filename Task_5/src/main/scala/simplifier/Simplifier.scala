package simplifier

import AST._
import scala.language.postfixOps
import Flatter._

// to implement
// avoid one huge match of cases
// take into account non-greedy strategies to resolve cases with power laws
object Simplifier {

  type Simplify[T] = PartialFunction[T, Node]

  def simplify(n:Node) = simplifyFlat(flatten(n))

  def simplifyFlat(n:Node):Node = n childMap simplifyFlat match {
    case n:NodeList => simplifyNodeList(n)
    case b:BinExpr => simplifyBinExpr(b)
    case u:Unary => simplifyUnary(u)
    case c:ConditionalInstr => simplifyConditionalInstr(c)
    case i:IfElseExpr => simplifyIfElseExpr(i)
    case a:Assignment=> simplifyAssignment(a)
    case w:WhileInstr => simplifyWhileInstr(w)
    case f:FlatNode => simplifyFlatNode(f)
    case n:Node => n
  }

  lazy val simplifyFlatNode:Simplify[FlatNode] = {
    case f:FlatArithmeticExpr => simplifyFlatArithmeticExpr(f)
  }
  def simplifyFlatArithmeticExpr(f:FlatArithmeticExpr):Node = f match {
    case FlatArithmeticExpr(c, o) => FlatArithmeticExpr(
      c
        .filter(_._2 != 0)
        .foldLeft[List[(Node, Int)]]((IntNum(0), 1) :: Nil) {
          case ((IntNum(s), cnt) :: tail, (IntNum(i), x)) => (IntNum(s + i * x), cnt) :: tail
          case ((Num(s), cnt) :: tail, (Num(i), x)) => (FloatNum(s + i * x), cnt) :: tail
          case (head :: tail, e) => head :: e :: tail
        }
        .toMap
        .filter(_._1 != (o match {
          case ArithmOpPair("+", "-") => IntNum(0)
          case ArithmOpPair("*", "/") => IntNum(1)
          case _ => None
        }))
      , o)
  }





  lazy val simplifyAssignment:Simplify[Assignment] = {
    case Assignment(l, r) if l == r => NodeList()
    case Assignment(l, r) => Assignment(l, r)
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

  lazy val simplifyWhileInstr:Simplify[WhileInstr] = {
    case WhileInstr(FalseConst, _) => NodeList()
    case WhileInstr(cond, body) => WhileInstr(cond, body)
  }

  lazy val simplifyConditionalInstr:Simplify[ConditionalInstr] = {
    case ConditionalInstr(l, d) if l exists (_.condition == TrueConst) => l.find(_.condition == TrueConst).get.suite
    case ConditionalInstr(l, d) if l forall (_.condition == FalseConst) => d getOrElse NodeList()
    case ConditionalInstr(l, d) => ConditionalInstr(l, d)
  }

  lazy val simplifyIfElseExpr:Simplify[IfElseExpr] = {
    case IfElseExpr(TrueConst, l, r) => l
    case IfElseExpr(FalseConst, l, r) => r
    case IfElseExpr(cond, l, r) => IfElseExpr(cond, l, r)
  }

  type BinExprTuple = (String, Node, Node)
  def simplifyBinExpr(b:BinExpr) = b match {
    case BinExpr(op, l, r) => simplifyBinExprMatch(op, l, r)
  }

  lazy val simplifyBinExprMatch:Simplify[BinExprTuple] = {
    //concat tuples
    case ("+", Tuple(l1), Tuple(l2)) => Tuple(l1 ++ l2)

    //concat lists
    case ("+", ElemList(l1), ElemList(l2)) => ElemList(l1 ++ l2)

    //recognize power laws
    case ("*", BinExpr("**", a, b), BinExpr("**", c, d)) if a == c => simplifyBinExprMatch("**", a, simplifyBinExprMatch("+", b, d))
    case ("**", BinExpr("**", a, b), c) => simplifyBinExprMatch("**", a, simplifyBinExprMatch("*", b, c))
    case ("**", a, IntNum(0)) => 1
    case ("**", a, IntNum(1)) => a
    case ("+",
      BinExpr(op@("+"|"-"),
      BinExpr("**", a,IntNum(2)),BinExpr("*",BinExpr("*",IntNum(2),b),c)),BinExpr("**",d,IntNum(2)))
      if a == b && c == d =>
      simplifyBinExprMatch("**", simplifyBinExprMatch(op, a, c), 2)
    case ("-",
      BinExpr("-", BinExpr("**",BinExpr("+",a,b),IntNum(2)),BinExpr("**",a1,IntNum(2))),
      BinExpr("*",BinExpr("*",IntNum(2),a2),b1))
      if a == a1 && a1 == a2 && b == b1
      => simplifyBinExprMatch("**", b, 2)
    case ("-",BinExpr("**",BinExpr("+",a,b),IntNum(2)),BinExpr("**",BinExpr("-",a1,b1),IntNum(2)))
      if a == a1 && b == b1
      => simplifyBinExprMatch("*", simplifyBinExprMatch("*", 4, a), b)

    //eval known exprs
    case (op, IntNum(a), IntNum(b)) => evalBinExpr(op, a, b).toInt
    case (op, Num(a), Num(b)) => evalBinExpr(op, a, b)

    //understand distributive property of multiplication
    case (op@("+"|"-"), BinExpr("*", a, b), BinExpr("*", c, d)) if Set(a, b) intersect Set(c, d) nonEmpty
      =>
        val (x, y) = (Set(a, b), Set(c, d))
      simplifyBinExprMatch("*", x & y last, simplifyBinExprMatch(op, x -- (x & y) last, y -- (x & y) last))
    case (op@("+"|"-"), a, o@BinExpr("*", b, c)) if a == b || a == c
      => simplifyBinExprMatch(op, simplifyBinExprMatch("*", a, 1), o)

    //simplify easy exprs
    //case (op, IntNum(0), x) if "+" :: "and" :: Nil contains op => x
  }


  lazy val evalBinExpr = PartialFunction[(String, Double, Double), Double] {
    case ("**", a, b) => math.pow(a, b)
    case ("+", a, b) => a + b
    case ("-", a, b) => a - b
    case ("*", a, b) => a * b
    case ("/", a, b) => a / b
  }

  lazy val simplifyUnary:Simplify[Unary] = {
    case Unary("not", TrueConst) => FalseConst
    case Unary("not", FalseConst) => TrueConst
    case Unary("not" | "-", Unary("not" | "-", v)) => v
    case u => u
  }

}