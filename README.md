# FCurve-Cleaner

## What does it do?

It tries to clean your dense animation graphs (like mocap graphs) like an animator would! So it will produce a usable artist friendly result while maintaining the original graph (leveraging the power of bezier curves).

  

![Before And After](https://i.ibb.co/sPMq1mt/graph-before.jpg)

## ***You are in control!***
 
And the best part is that you have the control to specify how much detail you want to preserve from the original curve via tolerance sliders. The lower the tolerance, the more points from the original FCurve will be selected (more on this later). 
For more control over precisions on different areas of the curve, you can manually select different ranges of keyframes to clean with different precisions. For example 

![different tolerances](https://i.ibb.co/yFY0Mbf/control-original.jpg)


## How can I use it?

**1- Install Dependency**  
The addon uses a function from *scipy* library which is not included in the blender's python by default. So you should install this library to use this addon.
Steps for installation (only for the first time):
 1. Go to blender's installation folder and right click on *blender.exe* and choose *run by administer*.
 2. Install the addon
 3. click on ***install dependency*** (which will appear on addon's info)
After clicking the install button, it should take a minute or two to install it. You can open the console window before hitting the install button to view the installation progress.

**2- Select your fcurve (or check *all fcurves* option)**  
Unless you've checked the ***clean all of fcurves for action*** box, you should select the fcurve you want to clean. 
If the ***clean all of fcurves for action*** option is checked, it will clean all the fcurves for the active action. 

**3- select keyframes to clean**  
There are 3 methods to choose which frames to clean
 - Scene Frame Range
	 - Uses the scene frame range. 
 - Specified Frame Range
	 - If you choose this method, two sliders will show up for you to choose your frame range.
 - Selected Keyframes
	 - Basically uses the first and the last selected keyframe on selected fcurve to choose the frame range for cleaning. (should improve) 

**4- clean!**  
Find the clean fcurve panel in graph editor ...
You are now ready to clean your graph. Just hit the ***Clean Fcurve*** button to begin the cleaning operation.
If the number of chosen frames are high, it might take a while to clean them and Blender would freeze during that operation. So I suggest that before you hit the clean button,  open up the console to see the cleaning progress.

## How does it work?  
It cleans the curve in 3 passes. First it selects the keyframes. Then it selects the inbetweens and the Final pass is for determining the locations of bezier control handles.
For the first two passes, it uses the keyframe and inbetweens precision sliders respectively to detect changes and select points.
