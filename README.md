# Mujoco Modeler
GUI for adjusting the geometry of Mujoco models

## How it works?
Use mouse right button to select a geometry of a bone or just the bone itself when it has no geometry. Then you can rotate, translate, change the size of
it. And you can also add new geometry to the bone or delete existing geometry. Currently it supports two types of geometry in Mujoco: **capsule** and **ellipsoid**.

You can also use the script **mujoco_view.py** to view the model in Mujoco.

## keyboard shortcuts
| Key           | Functionality |
| ------------- | ------------- |
| q w e a s d   | rotate the geometry |
| u i o j k l   | translate the geometry |
| U I O J K L   | change the radius of ellipsoid (only works for ellipsoid) |
| up down       | change the radius of the capsule (only works for capsule) |
| left right    | change the length of the capsule (only works for capsule) |
| r             | create a new capsule for the bone |
| t             | create a new ellipsoid for the bone |
| c             | clone currently selected geometry |
| d             | delete currently selected geometry |
| v             | export modified model to xml file |
| `             | quit the program|

