/**
  * Created by mathek on 28/12/2016.
  */

import AST._
import simplifier.Simplifier._

object PrintAST extends App {
  val p = new Parser()
  val in =
    """-x + x + y + z + 0 + 2 + 3
    """.stripMargin
  p.parse(p.program, in) match {
    case p.Success(result:List[Node], _) => println(simplify(result))
  }


}