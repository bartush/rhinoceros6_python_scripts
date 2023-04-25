
import rhinoscriptsyntax as rs


def AddBlockDefinition(object_ids, block_name, base_point=[0,0,0], description=None, URL_description=None, URL=None, replace_block=False, keep_objects=False):
    """ Turns a list of objects into a block definition.
    This script batches the Rhino Command.
    - Scripted by Martin Manegold for imagine -
    Parameters:
      object_ids = list of object IDs (Guids)
      block_name = the name for the new block Definition
      base_point[op] = base point of the new block
      description[opt] = the description of the block.
      URL_description[opt] = the URL description of the block.
      URL[opt] = the URL of the block.     
      replace_block[opt] = if true an existing block with the same name is replaced
      keep_objects[opt] = if true the input objects are kept
     Returns:
      the name of the block definition
      None on Error   
     """
    #Check if the block already exists
    if rs.IsBlock(block_name) and not replace_block:
        #The block already exists
        return block_name
    #Make sure the current clane is the world CPlane
    CPlane_store = rs.ViewCPlane()
    rs.ViewCPlane(rs.CurrentView(), rs.WorldXYPlane())
    base_point = rs.coerce3dpoint(base_point)
    #Select the Objects
    rs.UnselectAllObjects()
    if keep_objects:
        object_ids = rs.CopyObjects(object_ids)
    rs.SelectObjects(object_ids)
    #Initialize command
    command = ""   
    #Start command
    command += "-_block "
    #Add Base Point   
    command += "%d,%d,%d " %(base_point.X, base_point.Y, base_point.Z)
    #Add block name
    command += block_name + " "
    #Check if the block needs to be replaced
    if rs.IsBlock(block_name):
        command += "y "       
    #Add block description
    if description:
        command += "\" %s\" " % (description)
    else:
        command += "_Enter "
    #Block URL Description
    if URL_description:
        command += "\" %s\" " % (URL_description)
    else:
        command += "_Enter "
    #Block URL
    if URL:
        command += "\" %s\" " % (URL)
    else:
        command += "_Enter "
    #Execute command
    rs.Command(command, False)
    #Get the last created objects
    created_objects = rs.LastCreatedObjects()
    #Delete block instance
    rs.DeleteObject(created_objects[2])
    #Make sure the current Clane is the World CPlane
    rs.ViewCPlane(rs.CurrentView(), CPlane_store)
    return block_name 