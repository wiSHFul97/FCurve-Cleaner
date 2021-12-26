import bpy
from .clean_graph_utils import get_cleaning_kf_index_range, get_lr_exterms_kf_inds \
	, find_inbetween_points, distance_func, calculate_apply_curve_handles
import numpy as np


class GRAPH_OT_clean_graph(bpy.types.Operator):
	"""Clean Animation FCurve"""
	bl_idname = "graph.clean_fcurve"
	bl_label = "Clean FCurve"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		# return True
		return context.area.type == 'GRAPH_EDITOR'
	
	def execute(self, context):
		scene = context.scene
		fcurve = context.active_editable_fcurve
		if fcurve is None:
			raise 'select an fcurve!' # TODO unless it is for all fcurves
		keyframe_tol = scene.keyframes_tolerance
		inbetween_tol = scene.inbetweens_tolerance

		# get clean KFs range
		start, finish = list(map(lambda x:x[0], get_cleaning_kf_index_range(context, scene.frame_selection, fcurve)))
		kf_points = fcurve.keyframe_points
		points = list(map(lambda x:(x[0],x[1].co), kf_points.items()))
		points.sort(key=lambda x: x[0])

		# first pass: select extermums as KFs
		selected_kf_inds = [start, finish]
		selected_kf_inds.extend(get_lr_exterms_kf_inds(points, start, finish, anomaly_tol=keyframe_tol))
		a = [(points[ind][0], points[ind][1].x) for ind in selected_kf_inds]
		print("first pass keyframes***********")
		print(a, len(a))

		# second pass: find inbetween points
		selected_kf_inds.sort()
		inbetween_points_inds = find_inbetween_points(selected_kf_inds, points, inbetween_tol)
		print("second pass keyframe----------------")
		a = [(points[ind][0], points[ind][1].x) for ind in inbetween_points_inds]
		print(a, len(a))
		print("------------------------------------")

		# third pass: find curve handles
		selected_points = np.array(sorted(list(set(selected_kf_inds + inbetween_points_inds))))
		calculate_apply_curve_handles(selected_points, kf_points, points)

		return {'FINISHED'}

def register():
	Scene = bpy.types.Scene
	Scene.frame_selection = bpy.props.EnumProperty (
		name='Clean Frame Range',
		description='Choose frame selection method to clean them!',
		items = {
			('scene', 'Scene Frame Range', 'Use scene frame range'),
			('selected', 'Selected Keyframes', 'Use selected KFs in graph editor'),
			('specify', 'Specify Keyframes', 'Use the specified range'),
		},
		default='scene',
	)
	Scene.start_frame = bpy.props.IntProperty (
		name='Clean Start Frame',
		description='start frame to clean',
		default=0,
		min=0,
		soft_max=1000,
	)
	Scene.end_frame = bpy.props.IntProperty (
		name='Clean End Frame',
		description='end frame to clean',
		default=50,
		min=1,
		soft_max=1000,
	)
	Scene.keyframes_tolerance = bpy.props.FloatProperty (
		name='Keyframes Tolerance',
		description='Tolerance for Detecting Keyframes',
		default=.3,
		min=0.0,
		soft_max=1.0,
	)
	Scene.inbetweens_tolerance = bpy.props.FloatProperty (
		name='Inbetweens Tolerance',
		description='Tolerance for Detecting Inbetween Poses',
		default=.4,
		min=0.0,
		soft_max=1.0,
	)
	bpy.utils.register_class(GRAPH_OT_clean_graph)

def unregister():
	bpy.utils.unregister_class(GRAPH_OT_clean_graph)
	Scene = bpy.types.Scene
	Scene.frame_selection = None
	Scene.start_frame = None
	Scene.end_frame = None
	Scene.keyframes_tolerance = None
	Scene.inbetweens_tolerance = None
