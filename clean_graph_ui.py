import bpy


class VIEW3D_PT_clean_graph_ui(bpy.types.Panel):
	"""Control Panel of Clean FCurve"""
	bl_label = "Clean FCurve"
	bl_category = 'Clean FCurve'
	bl_space_type = 'GRAPH_EDITOR'
	bl_region_type = 'UI'

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		layout.operator("graph.clean_fcurve")
		layout.prop(scene, 'frame_selection')
		if scene.frame_selection == 'specify':
			layout.label(text="Specify Frame Range:")
			row1 = layout.row(align=True)
			row1.prop(scene, 'start_frame', slider=True)
			row1.prop(scene, 'end_frame', slider=True)
		layout.label(text="Tolerances:")
		row = layout.row()
		row.prop(scene, 'keyframes_tolerance')
		row.prop(scene, 'inbetweens_tolerance')


def register():
	print('rrrrrrrrrrrrrrrrrrrrrrrrrr')
	bpy.utils.register_class(VIEW3D_PT_clean_graph_ui)

def unregister():
	print('uuuuuuuuuuuuuuuuuuuuuuuu')
	bpy.utils.unregister_class(VIEW3D_PT_clean_graph_ui)

