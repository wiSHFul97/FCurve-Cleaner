import bpy


class VIEW3D_PT_clean_graph_ui(bpy.types.Panel):
	"""Control Panel of Clean Graph"""
	bl_label = "Clean Graph"
	bl_category = 'Clean Graph'
	bl_space_type = 'GRAPH_EDITOR'
	bl_region_type = 'UI'

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		layout.operator("graph.clean_graph")
		layout.prop(scene, 'frame_selection')
		if scene.frame_selection == 'specify':
			layout.label(text="Specify Frame Range:")
			row1 = layout.row(align=True)
			row1.prop(scene, 'start_frame', slider=True)
			row1.prop(scene, 'end_frame', slider=True)
		layout.label(text="Precisions:")
		row = layout.row()
		row.prop(scene, 'keyframes_precision')
		row.prop(scene, 'inbetweens_precision')


def register():
    # bpy.utils.register_class(VIEW3D_PT_clean_graph_ui)
	pass

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_clean_graph_ui)

