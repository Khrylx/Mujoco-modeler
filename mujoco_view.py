from mujoco_py import load_model_from_path, MjSim, MjViewer

model = load_model_from_path('data/my_humanoid.xml')
sim = MjSim(model)
viewer = MjViewer(sim)
t = 0

sim.data.qpos[2] += 1.0
sim.forward()
while True:
    t += 1
    # sim.data.ctrl[:] = 0.05
    # sim.step()
    viewer.render()
