# The geometry of somatosensory representations in the cortex

code for the paper "The geometry of somatosensory representations in the cortex"
## Abstract
The well-known body map of the primary somatosensory cortex (S1), known as the homunculus, is spatially organized such that cortical areas sensitive to body parts, from head to toes, are organized from lateral to medial. Another way of characterizing somatosensory responses in the cortex is to consider them in the framework of the hierarchical nature of somatosensory information processing. Moving from rostral to caudal within S1, cortical responses become less selective, more bilateral, and more complex. This approximate orthogonality of body and hierarchy directions may allow the cortex to process information about each body part at multiple hierarchy levels. Body maps and hierarchies have also been identified in other regions in the somatosensory cortex. However, the geometric relationships between body representation and hierarchy have remained unclear because a unified description of these measures across the entire cortex has been lacking. Here we used functional MRI to characterize cortical responses to full-body light touch stimulation. We show that the orthogonal relationship between body representation and hierarchy in S1, does not generalize to the entire somatosensory cortex. Rather, it is a pinhole observation of a radial geometry of both the body representations and the hierarchy. Our findings are consistent with established body maps and hierarchies, but offers a holistic, macroscopic view of the organization of these maps  with respect to each other. Similar organizational patterns in the visual and auditory systems suggest that radial topography may be a common feature across sensory systems.

![](data/body-selectivity-s1-lh.jpg)
*body-selectivity angles between gradient maps left hemisphere inflated*

![](data/Selectivity-pial-lh.jpg)
*Selectivity map left hemisphere pial*

## Code
main function to calculate angle maps between body selectivity and laterality is in gradient_maps.py.
The functions uses selectivity with 800 smooth factor, laterality with 400 and body with 200.
The python script draw_data_map.py is a tool for presenting data maps in 3D using nilearm.

![](data/body-sphere-lh.jpg)
*body map left hemisphere sphere*
## Acknowledgements

<img src="data/body-sel-lh_hist.png" width="200">

*body selectivity histogram left hemisphere*

## nilearn
To support non symmetrical data around 0 we made changes to the nilearn library and is available in the nilearn folder.

## Data
Subjects fMRI data is available at
