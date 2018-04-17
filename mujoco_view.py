from mujoco_py import load_model_from_path, MjSim, MjViewer
import argparse

parser = argparse.ArgumentParser(description='Mujoco Modeler')
parser.add_argument('--input', default="data/humanoid.xml", metavar='G',
                    help='input path of the model')
args = parser.parse_args()

model = load_model_from_path(args.input)
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
