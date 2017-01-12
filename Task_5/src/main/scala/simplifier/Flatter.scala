package simplifier

import scala.language.postfixOps
import Simplifier._
import AST._

/**
  * Created by mathek on 12/01/2017.
  */

object Flatter {

  sealed trait FlatNode extends SimplifierNode {
    override def toStr = toString
  }

  def flatten(n: Node):Node = n match {
    case FlatArithmeticExpr.FromExpr(e) => e
    case node => node childMap flatten

  }

  case class ArithmOpPair(posOp:String, negOp:String) {
    val valueOf: String => Boolean = {
      case `posOp` => true
      case `negOp` => false
      case _ => throw new IllegalArgumentException()
    }
  }
  object ArithmOpPair {
    val validPairs = (("+", "-") :: ("*", "/") :: Nil) flatMap {
      case (p, n) => Map(p -> ArithmOpPair(p, n), n -> ArithmOpPair(p, n))
    } toMap
  }
  case class FlatArithmeticExpr(content:Map[Node, Int], opPair:ArithmOpPair) extends FlatNode {
    def + (s:Node) = s match {
      case FlatArithmeticExpr(other_content, `opPair`) => joinContent(other_content)
      case s:Node => joinContent(Map(s -> 1))
    }
    def - (s:Node) = s match {
      case f:FlatArithmeticExpr => this + -f
      case s:Node => joinContent(Map(s -> -1))
    }
    def unary_- = FlatArithmeticExpr(content map {case (s, x) => (s, -x)}, opPair)
    private def joinContent(other:Map[Node, Int]) = FlatArithmeticExpr(
      (content.keySet ++ other.keySet) map { k => (k, content.getOrElse(k, 0) + other.getOrElse(k, 0))} toMap,
      opPair
    )

    val childMap:NodeMap = f => FlatArithmeticExpr(content map {case (n, i) => (f(n), i) }, opPair)
  }
  object FlatArithmeticExpr {
    object FromExpr {
      def unapply(expr: Expr): Option[FlatArithmeticExpr] =
        ArithmOpPair.validPairs get expr.op map { opPair =>
          expr match {
            case BinExpr(op, l, r) =>
              val (base, fl, fr) = (FlatArithmeticExpr(Map.empty, opPair), flatten(l), flatten(r))
              if (opPair valueOf op) base + fl + fr else base + fl - fr
            case Unary(op, e) =>
              val (base, fe) = (FlatArithmeticExpr(Map.empty, opPair), flatten(e))
              if (opPair valueOf op) base + fe else base - fe
          }
        }
    }
  }
}
