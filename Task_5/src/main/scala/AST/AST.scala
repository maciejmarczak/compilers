package AST

object Priority {
  val binary = Map("lambda"->1,
    "or"->2,
    "and"->3,
    "is"->8, "<"->8, ">"->8, ">="->8, "<="->8, "=="->8, "!="->8,
    "+"->9,  "-"->9,
    "*"->10, "/"->10, "%"->10,
    "**" -> 11
  )

  val unary = Map("not"->4,
          "+"->12,  "-"->12)
}

sealed trait Node {
  def toStr:String
  val indent = " " * 4
  type NodeMap = (Node => Node) => Node
  val childMap: NodeMap
}

sealed trait LeafNode extends Node{
  val childMap:NodeMap = f => this
}

trait SimplifierNode extends Node {
  def toStr = ""
}

sealed trait Num extends LeafNode {
  def v:Double = this match {
    case IntNum(x) => x.toDouble
    case FloatNum(x) => x
  }
}

object Num {
  def unapply(n: Num): Option[Double] = Some(n.v)
}

case class IntNum(value: Int) extends Num {
  def toStr = value.toString
}

case class FloatNum(value: Double) extends Num {
  def toStr = value.toString
}

case class StringConst(value: String) extends LeafNode {
  def toStr = value
}

case object TrueConst extends LeafNode {
  def toStr = "True"
}

case object FalseConst extends LeafNode {
  def toStr = "False"
}

case class Variable(name: String) extends LeafNode {
  def toStr = name
  def mapSelf(f:Node => Node) = this
}

sealed trait Expr extends Node {
  val op:String
  val expr:Node
}

case class Unary(op: String, expr: Node) extends Expr {

  def toStr = {
    var str  = expr.toStr
    expr match {
      case e@BinExpr(_,_,_) => if(Priority.binary(e.op)<=Priority.unary(op)) { str = "(" + str + ")" }
      case e@Unary(_,_) => if(Priority.unary(e.op)<=Priority.unary(op)) { str = "(" + str + ")" }
      case _ =>
    }
    op + " " + str
  }

  val childMap:NodeMap = f => Unary(op, f(expr))
}

case class BinExpr(op: String, left: Node, right: Node) extends Expr {

  val expr:NodeList = List(left, right)

  def toStr = {
    var leftStr  = left.toStr
    var rightStr = right.toStr
    left match {
      case l@(_:BinExpr) => if(Priority.binary(l.op)<Priority.binary(op)) { leftStr = "(" + leftStr + ")" }
      case l@(_:Unary) => if(Priority.unary(l.op)<Priority.binary(op)) { leftStr = "(" + leftStr + ")" }
      case _ =>
    }
    right match {
      case r@BinExpr(_,_,_) => if(Priority.binary(r.op)<Priority.binary(op)) { rightStr = "(" + rightStr + ")" }
      case r@Unary(_,_) => if(Priority.unary(r.op)<Priority.binary(op)) { rightStr = "(" + rightStr + ")" }
      case _ =>
    }
    leftStr + " " + op + " " + rightStr
  }

  val childMap:NodeMap = f => BinExpr(op, f(left), f(right))
}

case class IfElseExpr(cond: Node, left: Node, right: Node) extends Node {

  def toStr = left.toStr + " if " + cond.toStr + " else " + right.toStr

  val childMap:NodeMap = f => IfElseExpr(f(cond), f(left), f(right))
}

case class Assignment(left: Node, right: Node) extends Node {
  def toStr = left.toStr + " = " + right.toStr
  val childMap:NodeMap = f => Assignment(f(left), f(right))
}

case class Subscription(expr: Node, sub: Node) extends Node {
  def toStr = expr.toStr + "[" + sub.toStr + "]"
  val childMap:NodeMap = f => Subscription(f(expr), f(sub))
}

case class KeyDatum(key: Node, value: Node) extends Node {
  def toStr = key.toStr + ": " + value.toStr
  val childMap:NodeMap = mapSelf
  def mapSelf(f:Node => Node) = KeyDatum(f(key), f(value))
}

case class GetAttr(expr:Node, attr: String) extends Node {
  def toStr = expr.toStr + "." + attr
  val childMap:NodeMap = f => GetAttr(f(expr), attr)
}

case class ConditionSuitePair(blockType: String, condition: Node, suite: Node) extends Node {
  def toStr = blockType + " " + condition.toStr + ":\n" + suite.toStr.replaceAll("(?m)^", indent)
  val childMap:NodeMap = mapSelf
  def mapSelf(f:Node => Node) = ConditionSuitePair(blockType, f(condition), f(suite))
}

case class ConditionalInstr(condition_suites: List[ConditionSuitePair], default: Option[Node]) extends Node {
  def toStr =
    condition_suites.map(_.toStr).mkString("\n") +
    default.map("\nelse:\n" + _.toStr.replaceAll("(?m)^", indent)).getOrElse("")
  val childMap:NodeMap = f => ConditionalInstr(condition_suites map (_ mapSelf f), default map f)
}

case class WhileInstr(cond: Node, body: Node) extends Node {
  def toStr = {
    "while " + cond.toStr + ":\n" + body.toStr.replaceAll("(?m)^", indent)
  }
  val childMap:NodeMap = f => WhileInstr(f(cond), f(body))
}

case class InputInstr() extends LeafNode {
  def toStr = "input()"
}

case class ReturnInstr(expr: Node) extends Node {
  def toStr = "return " + expr.toStr
  val childMap:NodeMap = f => ReturnInstr(f(expr))
}

case class PrintInstr(expr: Node) extends Node {
  def toStr = "print " + expr.toStr
  val childMap:NodeMap = f => PrintInstr(f(expr))
}

case class FunCall(name: Node, args_list: Node) extends Node {

  def toStr = {
    args_list match {
      case NodeList(list) => name.toStr + "(" + list.map(_.toStr).mkString("", ",", "") + ")"
      case _ => name.toStr + "(" + args_list.toStr + ")"
    }
  }

  val childMap:NodeMap = f => FunCall(name, args_list childMap f)
}

case class FunDef(name: String, formal_args: Node, body: Node) extends Node {
  def toStr = {
    var str = "\ndef " + name + "(" + formal_args.toStr + "):\n"
    str += body.toStr.replaceAll("(?m)^", indent) + "\n"
    str
  }
  val childMap:NodeMap = f => FunDef(name, f(formal_args), f(body))
}

case class LambdaDef(formal_args: Node, body: Node) extends Node {
  def toStr = "lambda " + formal_args.toStr + ": " + body.toStr
  val childMap:NodeMap = f => LambdaDef(f(formal_args), f(body))
}
    
case class ClassDef(name: String, inherit_list: Node, suite: Node) extends Node {
  def toStr = {
    val str = "\nclass " + name
    var inheritStr = ""
    val suiteStr = ":\n" + suite.toStr.replaceAll("(?m)^", indent)
    inherit_list match {
      case NodeList(x) => if(x.length>0) inheritStr = "(" + x.map(_.toStr).mkString("", ",", "") + ")" 
      case _ =>
     }
     str + inheritStr + suiteStr
  }
  val childMap:NodeMap = f => ClassDef(name, f(inherit_list), f(suite))
}

case class NodeList(list: List[Node] = Nil) extends Node {
  def toStr = {
    list.map(_.toStr).mkString("", "\n", "")
  }
  val childMap:NodeMap = f => list map f
}

case class KeyDatumList(list: List[KeyDatum]) extends Node {
  def toStr = list.map(_.toStr).mkString("{", ",", "}")
  val childMap:NodeMap = f => KeyDatumList(list map (_ mapSelf f))
}

case class IdList(list: List[Variable]) extends Node {
  def toStr = list.map(_.toStr).mkString("", ",", "")
  val childMap:NodeMap = f => IdList(list map (_ mapSelf f))
}

case class ElemList(list: List[Node]) extends Node {
  def toStr = list.map(_.toStr).mkString("[", ",", "]")
  val childMap:NodeMap = f => ElemList(list map f)
}

case class Tuple(list: List[Node]) extends Node {
  def toStr = list.map(_.toStr).mkString("(", ",", ")")
  val childMap:NodeMap = f => Tuple(list map f)
}
