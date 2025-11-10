import maya.cmds as cmds

def post_process(objects, delete_history, center_pivot):
    if not isinstance(objects, list):
        objects = [objects]

    for obj in objects:
        if delete_history:
            cmds.delete(obj, constructionHistory=True)
        if center_pivot:
            cmds.xform(obj, centerPivots=True)

def separate_logic(selection, prefix, delete_history, center_pivot):
    if not selection:
        cmds.warning("Please select at least one mesh object to separate.")
        return None, 0

    all_separated_objects = []
    total_processed_count = 0
    original_selection_count = len(selection)

    for target_object in selection:
        shape_nodes = cmds.listRelatives(target_object, shapes=True, type='mesh', fullPath=True)

        if not shape_nodes:
            cmds.warning(f"Skipping '{target_object.split('|')[-1]}' as it is not a valid mesh object.")
            continue

        try:
            separated_objects = cmds.polySeparate(target_object, constructionHistory=False)
            if not separated_objects:
                cmds.warning(f"Could not separate '{target_object.split('|')[-1]}'. It might already be a single shell.")
                all_separated_objects.append(target_object) 
                continue
        except Exception as e:
            cmds.error(f"An error occurred during separation of '{target_object.split('|')[-1]}': {e}")
            continue

        print(f"Successfully separated '{target_object.split('|')[-1]}' into {len(separated_objects)} objects.")

        for obj in separated_objects:
            total_processed_count += 1
            newName = cmds.rename(obj, f"{prefix}_{total_processed_count:03}")
            all_separated_objects.append(newName)

    if not all_separated_objects:
        cmds.warning("No valid mesh objects were processed.")
        return None, original_selection_count

    post_process(all_separated_objects, delete_history, center_pivot)
    cmds.select(all_separated_objects, replace=True)
    
    return all_separated_objects, original_selection_count

def combine_logic(selection, prefix, delete_history, center_pivot):
    if len(selection) < 2:
        cmds.warning("Please select at least two mesh objects to combine.")
        return None
    
    valid_meshes = []
    
    for obj in selection:
        if cmds.listRelatives(obj, shapes=True, type='mesh', fullPath=True):
            valid_meshes.append(obj)
        else:
            cmds.warning(f"Skipping '{obj}' as it is not a valid mesh.")

    if len(valid_meshes) < 2:
        cmds.warning("Not enough valid mesh objects selected to perform a combine.")
        return None

    try:
        combined_result = cmds.polyUnite(valid_meshes, constructionHistory=True)
        combined_object = combined_result[0]
    except Exception as e:
        cmds.error(f"An error occurred during combination: {e}")
        return None

    print(f"Successfully combined {len(valid_meshes)} objects into '{combined_object}'.")

    final_name = cmds.rename(combined_object, prefix)
    
    post_process(final_name, delete_history, center_pivot)

    return final_name