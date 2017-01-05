/**
  * Created by mathek on 29/12/2016.
  */
import scala.language.implicitConversions
package object AST {
  implicit def listOfNodesToNodeList(list:List[Node]):NodeList = NodeList(list)
  implicit def nodeListToList(nl:NodeList):List[Node] = nl.list
  implicit def intToIntNum(i:Int):IntNum = IntNum(i)
  implicit def doubleToFloatNum(i:Double):FloatNum = FloatNum(i)
}
