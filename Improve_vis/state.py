from paraview.simple import *

# Load the VTK file
vtk_data = OpenDataFile("/Users/dhruvm/Desktop/Improve_vis/GraphMAE_pre/graph_points.vtk")
vtk_data.UpdatePipeline()

# Extract the VTK dataset
vtk_data = vtk_data.GetClientSideObject().GetOutputDataObject(0)

# Get all points from the dataset
num_points = vtk_data.GetNumberOfPoints()

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# Loop through each point to create a sphere and apply a texture
for i in range(num_points):
    # Get point coordinates
    x, y, z = vtk_data.GetPoint(i)


    # Create a sphere at the point location
    sphere = Sphere()
    sphere.Center = [x, y, z]
    sphere.Radius = 20  # Adjust size if needed
    # Properties modified on sphere1
    sphere.ThetaResolution = 100
    sphere.PhiResolution = 100
    # show data in view
    sphere1Display = Show(sphere, renderView1, 'GeometryRepresentation')

    # create a new 'Texture Map to Sphere'
    textureMaptoSphere1 = TextureMaptoSphere(registrationName='TextureMaptoSphere1', Input=sphere)
    textureMaptoSphere1.PreventSeam = 1  # Reduces visible texture seams


    # show data in view
    textureMaptoSphere1Display = Show(textureMaptoSphere1, renderView1, 'GeometryRepresentation')
    textureMaptoSphere1Display.Specular = 1.0

    # a texture
    pie_chart = CreateTexture('/Users/dhruvm/Desktop/Improve_vis/GraphMAE_pre/pie/pie_chart' + str(i+1) + '.png')

    # change texture
    textureMaptoSphere1Display.Texture = pie_chart

# Render all spheres
Render()