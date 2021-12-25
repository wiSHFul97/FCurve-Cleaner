from numpy.core.fromnumeric import mean
import bpy
from .clean_graph_utils import get_cleaning_kf_index_range, get_lr_exterms_kf_inds \
	, find_inbetween_points, distance_func
import numpy as np
import mathutils

class GRAPH_OT_clean_graph(bpy.types.Operator):
	"""Clean Animation Graph"""
	bl_idname = "graph.clean_graph"
	bl_label = "Clean Graph"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		# return True
		return context.area.type == 'GRAPH_EDITOR'

	# def invoke(self, context, event):
	# 	wm = context.window_manager
	# 	return wm.invoke_props_dialog(self)
	
	def execute(self, context):
		# code for clean graph
		scene = context.scene
		fcurve = context.active_editable_fcurve
		# object = context.active_object
		if fcurve is None:
			raise 'select an fcurve!' # TODO unless it is for all fcurves
		keyframe_precision = scene.keyframes_precision
		inbetween_precision = scene.inbetweens_precision
		# action = object.animation_data.action

		# get clean KFs range
		start, finish = list(map(lambda x:x[0], get_cleaning_kf_index_range(context, scene.frame_selection, fcurve)))
		kf_points = fcurve.keyframe_points
		points = list(map(lambda x:(x[0],x[1].co), kf_points.items()))
		points.sort(key=lambda x: x[0])

		# first pass: select extermums as KFs
		selected_kf_inds = [start, finish]
		selected_kf_inds.extend(get_lr_exterms_kf_inds(points, start, finish, anomaly_count=keyframe_precision))
		a = [(points[ind][0], points[ind][1].x) for ind in selected_kf_inds]
		print("first pass keyframes***********")
		print(a, len(a))

		# second pass: find interpolation points
		selected_kf_inds.sort()
		interpolation_points_inds = find_inbetween_points(selected_kf_inds, points, inbetween_precision)
		print("second pass keyframe----------------")
		a = [(points[ind][0], points[ind][1].x) for ind in interpolation_points_inds]
		print(a, len(a))
		# interpolation_points_inds.sort()
		print("------------------------------------")

		# third pass: find curve handles
		from scipy.optimize import minimize
		selected_points = np.array(sorted(list(set(selected_kf_inds + interpolation_points_inds))))
		for j in range(len(selected_points)-1):
			xys = [(x[1].x, x[1].y) for x in points[selected_points[j]:selected_points[j+1]+1]]
			x0, y0 = xys[0]
			x3, y3 = xys[-1]
			xys = list(zip(*xys))
			d_func = lambda params:distance_func(params, x0, y0, x3, y3, np.array(xys[0]), np.array(xys[1]))
			initial_guess = np.array([.8*x0+.2*x3, .8*y0+.2*y3, .8*x3+.2*x0, .8*y3+.2*y0])
			y_diff = max(xys[1])-min(xys[1])
			# TODO .000001
			# TODO ydiff?
			y_diff *= 2
			result = minimize(d_func, initial_guess, bounds=[(x0+.000001, x3), (y0-y_diff, y0+y_diff), (x0, x3-.000001), (y3-y_diff, y3+y_diff)])
			if result.success:
				fitted_params = result.x
				# print(selected_points[j], selected_points[j+1])
				print('results: ', fitted_params)
				for k in range(selected_points[j+1]-1, selected_points[j], -1):
					kf_points.remove(kf_points[k])
				kf_points[selected_points[j]].interpolation = 'BEZIER'
				kf_points[selected_points[j]].handle_right_type = 'FREE'
				kf_points[selected_points[j]].handle_right = mathutils.Vector(fitted_params[:2])
				# print('000000000000000000000000000000000', selected_points, j)
				selected_points -= selected_points[j+1]-selected_points[j]-1
				# print(selected_points, selected_points[j+1])
				# kf_points[selected_points[j]+1].interpolation = 'BEZIER'
				# kf_points[selected_points[j]+1].handle_left_type = 'FREE'
				# kf_points[selected_points[j]+1].handle_left = mathutils.Vector(fitted_params[2:])
				kf_points[selected_points[j+1]].interpolation = 'BEZIER'
				kf_points[selected_points[j+1]].handle_left_type = 'FREE'
				kf_points[selected_points[j+1]].handle_left = mathutils.Vector(fitted_params[2:])

			else:
				print("failed!!!!!!!!!!!!!!!!!!!!!!")

		return {'FINISHED'}

def register():
	# Action = bpy.types.Action
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
	Scene.keyframes_precision = bpy.props.FloatProperty (
		name='Keyframes Precision',
		description='Precision for Detecting Keyframes',
		default=.3,
		min=0.0,
		soft_max=1.0,
	)
	Scene.inbetweens_precision = bpy.props.FloatProperty (
		name='Inbetweens Precision',
		description='Precision for Detecting Inbetween Poses',
		default=.4,
		min=0.0,
		soft_max=1.0,
	)
	# bpy.utils.register_class(GRAPH_OT_clean_graph)

def unregister():
	bpy.utils.unregister_class(GRAPH_OT_clean_graph)
	Scene = bpy.types.Scene
	Scene.frame_selection = None
	Scene.start_frame = None
	Scene.end_frame = None
	Scene.keyframes_precision = None
	Scene.inbetweens_precision = None
