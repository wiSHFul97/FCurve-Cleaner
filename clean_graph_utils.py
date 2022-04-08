import bpy
from mathutils import Vector
import numpy as np

def shorten_the_range(points, period, from_start=False, is_min=True, tolerance=.2): 
	offset, start, end = (1, period[0], period[1]) if from_start else (-1, period[1], period[0])
	tolerance = -tolerance if is_min else tolerance
	current_limit = points[start+offset][1].y + tolerance
	last_exterm = start+offset
	for i in range(start+offset, end, offset):
		if (points[i][1].y == points[i+offset][1].y) or ((points[i][1].y > points[i+offset][1].y) ^ is_min):
			current_limit = points[i+offset][1].y + tolerance
			last_exterm = i+offset
			continue
		if not ((current_limit > points[i+offset][1].y) ^ is_min):
			break
	else:
		last_exterm = end
	return (last_exterm, period[1]) if from_start else (period[0], last_exterm)
	# return (i, period[1]) if from_start else (period[0], i) # TODO dorost kardane index ha (+- 1 nadashte bashe?)

# def shorten_the_range1(points, period, from_start=False, is_min=True, anomaly_count=2): 
# 	anomalies = 0
# 	offset, current, start, end = (1, period[0], period[0], period[1]) if from_start \
# 		else (-1, period[1], period[1], period[0])

# 	for i in range(start+offset, end+offset, offset):
# 		if (points[i][1].y == points[i+offset][1].y) or ((points[i][1].y > points[i+offset][1].y) ^ is_min):
# 			current = i+offset
# 		else:
# 			anomalies += 1
# 			if anomalies >= anomaly_count:
# 				break
# 	return (current, period[1]) if from_start else (period[0], current)

def break_range(points, range_start, point1, range_end, point2, anomaly_count):
	modified_r_ps = []
	point1_is_min = points[point1[0]-1][1].y > point1[1].y # TODO check exception (compare to start)

	# first_range = shorten_the_range(points, (range_start, point1[0]), from_start=False, is_min=point1_is_min, anomaly_count=anomaly_count)
	first_range = shorten_the_range(points, (range_start, point1[0]), from_start=False, is_min=point1_is_min, tolerance=anomaly_count)
	if first_range[1] - range_start >= 2:
		modified_r_ps.append((range_start, first_range[1]))

	# second_range_start = shorten_the_range(points, (point1[0], point2[0]), from_start=True, is_min=point1_is_min, anomaly_count=anomaly_count)
	# second_range_end = shorten_the_range(points, (point1[0], point2[0]), from_start=False, is_min=(not point1_is_min), anomaly_count=anomaly_count)
	second_range_start = shorten_the_range(points, (point1[0], point2[0]), from_start=True, is_min=point1_is_min, tolerance=anomaly_count)
	second_range_end = shorten_the_range(points, (point1[0], point2[0]), from_start=False, is_min=(not point1_is_min), tolerance=anomaly_count)
	if second_range_end[1] - second_range_start[0] >= 2:
		modified_r_ps.append((second_range_start[0], second_range_end[1]))

	# last_range = shorten_the_range(points, (point2[0], range_end), from_start=True, is_min=(not point1_is_min), anomaly_count=anomaly_count)
	last_range = shorten_the_range(points, (point2[0], range_end), from_start=True, is_min=(not point1_is_min), tolerance=anomaly_count)
	if range_end - last_range[0] >= 2:
		modified_r_ps.append((last_range[0], range_end))
	
	return modified_r_ps

def convert_to_straight_line(points, start, end): # TODO vector math with numpy
	slope = (points[end][1].y - points[start][1].y)/(points[end][1].x - points[start][1].x)
	start_x = points[start][1].x
	new_points = [(point[0]-start, Vector((point[1].x, point[1].y-(slope*(point[1].x-start_x))))) for point in points[start:end+1]]
	return new_points
	
# def get_min_max_kf_inds(points, start, end, anomaly_count=2):
# 	modified_r_periods = [(start, end)]
# 	selected_kf_inds = [start, end]
# 	# print("-------------------------")
# 	while len(modified_r_periods) > 0: # TODO or number of steps
# 		# print("mmmmm", modified_r_periods)
# 		remaining_periods = modified_r_periods.copy()
# 		modified_r_periods.clear()
# 		# for each remaining range: update modified_r_periods
# 		for period in remaining_periods:
# 			# print("p: ", period)
# 			range_start = period[0]
# 			range_end = period[1]+1
# 			point1 = min(points[range_start: range_end], key=lambda x:x[1].y)
# 			point2 = max(points[range_start: range_end], key=lambda x:x[1].y)
# 			# TODO min.y == max.y: constant - straight line
# 			selected_kf_inds.extend([point1[0], point2[0]])
# 			point1, point2 = (point1, point2) if point1[1].x < point2[1].x else (point2, point1)
# 			modified_r_periods.extend(break_range(points, range_start, point1, range_end, point2, anomaly_count))
# 	return selected_kf_inds

def get_lr_exterms_kf_inds(points, start, end, anomaly_tol=.2):
	selected_kf_inds = []
	prev_start = start
	prev_end = end
	while True:
		new_start, new_end = get_new_start_end(points, prev_start, prev_end, anomaly_tol=anomaly_tol)
		if new_end != new_start and new_end < new_start + 2:
			break
		elif new_end == new_start:
			selected_kf_inds.extend([new_start])
			break
		else:
			selected_kf_inds.extend([new_start, new_end])
		prev_start, prev_end = new_start, new_end

	return selected_kf_inds

def get_new_start_end(points, start, end, anomaly_tol=.2):
	last_frame_is_min = points[end-1][1].y > points[end][1].y
	new_end = shorten_the_range(points, (start, end), from_start=False, is_min=last_frame_is_min, tolerance=anomaly_tol)[1]

	first_frame_is_min = points[start+1][1].y > points[start][1].y
	new_start = shorten_the_range(points, (start, end), from_start=True, is_min=first_frame_is_min, tolerance=anomaly_tol)[0]
	
	return new_start, new_end

def get_kf_index_from_x_co(fcurve, *args):
	return list(filter(lambda x:x[1] in args, map(lambda x:(x[0], x[1].co[0]), fcurve.keyframe_points.items())))

def get_kf_index_range_from_frames(fcurve, start, end):
	near_frames = list(filter(lambda x:start<=int(x[1])<end, map(lambda x:(x[0], x[1].co[0]), fcurve.keyframe_points.items())))
	return near_frames[0], near_frames[-1]

def _get_index_range(selection_method, context, fcurve):
	scene = context.scene
	if selection_method == 'specify':
		start = scene.start_frame
		end = scene.end_frame
		if start >= end:
			return None
		index_range = get_kf_index_range_from_frames(fcurve, start, end)
	elif selection_method == 'scene':
		index_range = get_kf_index_range_from_frames(fcurve, scene.frame_start, scene.frame_end)
	elif selection_method == 'selected':
		# TODO bug: uses selected xs but checks with current fcurve points
		kfs = context.selected_editable_keyframes # list of kfs
		specified_kf_xs = list(map(lambda x:x.co.x, [kfs[0], kfs[-1]]))
		index_range = get_kf_index_from_x_co(fcurve, *specified_kf_xs)
	return index_range

def get_cleaning_kf_index_range(context, selection_method, fcurve):
	index_range = _get_index_range(selection_method, context, fcurve)
	if len(index_range) != 2:
		return None
		# raise Exception('Error in frame selection!')
	return index_range

def find_inbetween_points(selected_kf_inds, points, inbetween_precision):
	interpolation_points_inds = []
	for ind in range(len(selected_kf_inds)-1):
		range_start = selected_kf_inds[ind]
		end = selected_kf_inds[ind+1]
		if end - range_start < 2:
			continue
		straighted_points = convert_to_straight_line(points, range_start, end) # make indexes from zero
		# TODO why (len - 2) works?
		inds = get_lr_exterms_kf_inds(straighted_points, 0, len(straighted_points)-1, anomaly_tol=inbetween_precision)
		converted_inds = [range_start+point for point in inds] # convert back indexes: +=start
		interpolation_points_inds.extend(converted_inds)
	return interpolation_points_inds

def get_poly_coeficients(v, constant):
	x0, x1, x2, x3 = v
	vs = np.array([-x0+3*x1-3*x2+x3, 3*x0-6*x1+3*x2, -3*x0+3*x1])
	vs = np.tile(vs, len(constant)).reshape((len(constant),-1))
	return np.append(vs, (constant+x0).reshape((-1, 1)), axis=1)

def distance_func(params, x0, y0, x3, y3, xs, ys):
	x1, y1, x2, y2 = params
	x_coeffs = get_poly_coeficients([x0, x1, x2, x3], -xs)
	t = np.ones((x_coeffs.shape[0], 1))
	for i in range(len(x_coeffs)):
		# print("coeffs:", x_coeffs)
		ts = np.roots(x_coeffs[i])
		ts = ts[np.isreal(ts)].astype(np.float32)
		ts1 = ts[(ts<=1) & (0<=ts)]
		# print('Ts:', ts, len(ts1), ts1)
		# print(x_coeffs[i])
		# print(x0, x1, x2, x3)
		if len(ts1) > 1:
			ts1 = ts[(ts<1) & (0<ts)]
		t[i] = ts1
	y_coeffs = get_poly_coeficients([y0, y1, y2, y3], np.zeros((1, 1)))
	t_powers = t**np.arange(3, -1, -1)
	y = (y_coeffs @ np.transpose(t_powers)).flatten()
	return np.dot(ys - y, ys - y)

def calculate_apply_curve_handles(selected_points, kf_points, points):
	""" for each range: find curve handle points so that the 
	resulting bezier curve has the minimum distance to the samples """
	
	from scipy.optimize import minimize
	for j in range(len(selected_points)-1):
		print(int(100*j/len(selected_points)))
		xys = [(x[1].x, x[1].y) for x in points[selected_points[j]:selected_points[j+1]+1]]
		x0, y0 = xys[0]
		x3, y3 = xys[-1]
		xys = list(zip(*xys))
		# distance function to minimize
		d_func = lambda params:distance_func(params, x0, y0, x3, y3, np.array(xys[0]), np.array(xys[1]))
		initial_guess = np.array([.8*x0+.2*x3, .8*y0+.2*y3, .8*x3+.2*x0, .8*y3+.2*y0])
		y_diff = max(xys[1])-min(xys[1])
		y_diff *= 1.5 # TODO calculate the multiplier
		# TODO .000001
		result = minimize(d_func, initial_guess, bounds=[(x0+.000001, x3), (y0-y_diff, y0+y_diff), (x0, x3-.000001), (y3-y_diff, y3+y_diff)])
		if result.success:
			fitted_params = result.x
			# delete inbetween samples
			for k in range(selected_points[j+1]-1, selected_points[j], -1):
				kf_points.remove(kf_points[k])
			# apply the argmins to the graph
			kf_points[selected_points[j]].interpolation = 'BEZIER'
			kf_points[selected_points[j]].handle_right_type = 'FREE'
			kf_points[selected_points[j]].handle_right = Vector(fitted_params[:2])
			# update the indices (cause of kf deletions)
			selected_points -= selected_points[j+1]-selected_points[j]-1
			kf_points[selected_points[j+1]].interpolation = 'BEZIER'
			kf_points[selected_points[j+1]].handle_left_type = 'FREE'
			kf_points[selected_points[j+1]].handle_left = Vector(fitted_params[2:])
		else:
			print("failed!!!!!!!!!!!!!!!!!!!!!!")