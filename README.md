# Developing a bicycling infrastructure classification system for Greater Melbourne, Australia using OpenStreetMap
## Background

Policy-makers are looking to promote the uptake of bicycling as a healthy mode of travel that reduces the negative effects of traditional motorised transport (physical inactivity, air pollution, traffic congestion) and achieves sustainability goals. 
As an active form of mobility, bicycling improves physical and mental health and has long-term public health benefits.
However, there are a number of barriers that prevent people from riding a bike, including fears about riding alongside motor vehicle traffic and the lack of safe and appropriate bicycling infrastructure. 
For the strategic installation of safer bicycling infrastructure or the improvement of existing infrastructure, rigorous evidence-informed scientific studies are necessary, which in turn rely on high-quality bicycling data, which is scarce.

In this regard, one of the prerequisites is understanding the different types of bicycling infrastructure that exist in an urban area and create an inventory dataset that can form the basis of future bicycling-related research.
[OpenStreetMap](https://www.openstreetmap.org/#map=10/-37.9524/145.0806) (OSM) is a valuable open-source map database that contains transport infrastructure data among other things and has spatial coverage for almost the entire planet.
Hence, it is used extensively by researchers and planners and it helps develop methods that are transferable and thus can be replicated irrespective of the study area.
We, the [Sustainable Mobility and Safety Research Group](https://www.monash.edu/medicine/sphpm/units/traumaepi/sustainable-mobility-and-safety-research-group) (SMSR) at Monash University, Australia, have developed a classification process to classify existing bicycling infrastructure across Greater Melbourne, Australia.
We have derived knowledge from existing studies and calibrated our classification system to suit local tagging practices.

## Update

1. Roads which have associated bike lanes (usually protected) which are mapped separately by OSM contributors, should not be classified as mixed traffic (as was the case in the earlier version). Thus, we have decided to classify roads with associated bike infra mapped separately in a new category '0b. Associated bike infrastructure separately mapped'. However, it is not trivial to detect the associated bike lane/infrastructure type. Also, given that infrastructure is separately mapped and is classified already, it could cause duplication issues.
2. Some protected bike lanes (e.g. along St Kilda Road) were getting incorrectly classified as 'Dedicated bikepaths' given that they are mapped separately to the associated road in OSM. We can now classify such instances correctly.
3. We have also added a 'superclass' classification, which is a less granular classification, and clubs together similar but separate classes from the more granular classification system.

## Technology
  * Python
  * OpenStreetMap
  * Python packages
    * [OSMnx](https://osmnx.readthedocs.io/en/stable/user-reference.html)
    * [NetworkX](https://networkx.org/)
    * [geojson](https://pypi.org/project/geojson/)
    * [Shapely](https://shapely.readthedocs.io/en/stable/manual.html)
    * [Pandas](https://pandas.pydata.org/docs/index.html)
   
## How to implement in Python
  * Install the aforementioned Python packages as described in the links.
  * A settings.py file has been provided. This file contains a more holistic set of OSM tags that are not retrieved by default by OSMnx. Copy the contents of this file into your settings.py file under your osmnx folder/installation. Otherwise, the code will throw KeyError.
  * Run the Python codes provided.
      
## Sample results
*Distribution of different types of bicycling infrastructure at the link-level in Greater Melbourne.*

<p align="center">
  <img width="624" height="606" src="https://github.com/SustainableMobility/bicycling-infrastructure-classification/blob/main/GitHub_bikeinfra_GMEL.PNG?raw=true">
</p>

*Distribution of different types of bicycling infrastructure at the link-level in Inner Melbourne.*

<p align="center">
  <img width="624" height="606" src="https://github.com/SustainableMobility/bicycling-infrastructure-classification/blob/main/GitHub_bikeinfra_InnerMelbourne.PNG?raw=true">
</p>

*Distribution of bike paths and protected bike lanes in Inner Melbourne.*

<p align="center">
  <img width="624" height="606" src="https://github.com/SustainableMobility/bicycling-infrastructure-classification/blob/main/GitHub_bikeinfra_bikepathANDprotectedlane_InnerMelbourne.PNG?raw=true">
</p>

## Authors
The document has been prepared by **Dr Debjit Bhowmick** and **Assoc Prof Ben Beck** from the Sustainable Mobility and Safety Research (SMSR) Group at Monash University and **Paul Yacoumis** from the Victorian Department of Transport and Planning. 
For any queries, please contact Dr Debjit Bhowmick (Research Fellow, debjit.bhowmick@monash.edu) or Assoc Prof Ben Beck (Head of SMSR, ben.beck@monash.edu).

## Citation
If you are using this classification system for your work, we strongly recommend citing this repository using the 'Cite this repository' feature on GitHub (found on the right side when you open the repo). 
Alternatively, you may use the guidelines provided [here](https://www.ilovephd.com/how-do-you-cite-a-github-repository/).

### BibTeX
```
@misc{Sustainable_Mobility_and_Safety_Research_Group_Bicycling_infrastructure_classification_2023,
author = {{Sustainable Mobility and Safety Research Group, Monash University}},
title = {{Bicycling infrastructure classification using OpenStreetMap}},
url = {https://github.com/SustainableMobility/bicycling-infrastructure-classification},
doi = {https://doi.org/10.6084/m9.figshare.27059983.v1},
year = {2023}
}
```
>
### APA
```
Sustainable Mobility and Safety Research Group, Monash University. (2023). Bicycling infrastructure classification using OpenStreetMap. https://github.com/SustainableMobility/bicycling-infrastructure-classification
```
[![DOI](https://zenodo.org/badge/679530218.svg)](https://doi.org/10.6084/m9.figshare.27059983.v1)


_Note: OSM is a volunteered geographic information and is prone to occasional completeness and correctness issues, especially in the case of bicycling infrastructure due to inconsistent tagging practices. This can lead to occasional misclassification, especially if directly translated to other study areas, especially outside Australia._

