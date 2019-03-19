# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 12:28:19 2018

@author: Michael Goetz (m.goetz@dkfz-heidelberg.de)
"""

import glob
import os
import subprocess
import SimpleITK as sitk
import numpy as np
import lidcXmlHelper as xmlHelper

# Path to the command lines tools of MITK Phenotyping
path_to_executables=r"E:\Tools\MITK Phenotyping 2018-10-18\bin"
# Path to the folder that contains the LIDC-IDRI DICOM files
path_to_dicoms = r"P:\Goetz\Datenkollektive\Lungendaten\Nodules_LIDC_IDRI\DICOM"
# Path to the folder that contains the LIDC-IDRI XML files
path_to_xmls= r"P:\Goetz\Datenkollektive\Lungendaten\Nodules_LIDC_IDRI\XML\tcia-lidc-xml"
path_to_xmls= r"P:\Goetz\Datenkollektive\Lungendaten\Nodules_LIDC_IDRI\XML2"
# Output path where the generated NRRD and NIFTI files will be saved
path_to_nrrds =  r"P:\Goetz\Datenkollektive\Lungendaten\Nodules_LIDC_IDRI\new_nrrd_2"
# Output path where the genreated Planar Figures will be saved
path_to_planars= r"P:\Goetz\Datenkollektive\Lungendaten\Nodules_LIDC_IDRI\new_planars_2"
# Output path to the CSV-file that will contain the nodule characteristics. An existing will be appended
path_to_characteristics=r"P:\Goetz\Datenkollektive\Lungendaten\Nodules_LIDC_IDRI\characteristics_2.csv"
# Ouput path to an error file where errors will be logged. An existing file will be appended.
path_to_error_file=r"W:\Old\LungImages\LIDC-IDRI\conversion_error_2.txt"

planar_template=r"template.pf"

list_of_appendix=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

def write_error(msg, errorfile=path_to_error_file):
    """ 
    A simple error logging method. Errors should be reported using this functions.
    All errors are then logged in the file specified with the global variable
    'path_to_error_file' if no other file is specified.
    
    The error message is also printed in the main text. 
    """
    a=open(errorfile,'a')
    a.write(str(msg) + "\n")
    a.close()
    print("ERROR:",msg)

def get_dicom_from_study_uid(study_uid, series_uid):
    """
    Find the folder containing the dicoms that corresponds to a given study id
    or an study id and a series id.
    
    Returns:
        The path to the DICOMs matching the given IDs
        The number of DICOMs that had been found.
    """
    if series_uid is not None:
        search_path=os.path.join(path_to_dicoms, "*","*"+study_uid+"*","*"+series_uid+"*","*.dcm")
    else:
        search_path=os.path.join(path_to_dicoms, "*","*"+study_uid+"*","*","*.dcm")
    paths=glob.glob(search_path)
    if len(paths) > 0:
        return paths[0], len(paths)
    else:
        return [], 0
    
def create_nrrd_from_dicoms(image, patient_id):
    """
    Reads a folder that contains multiple DICOM files and 
    converts the input into a single nrrd file using a command line 
    app from MITK or MITK Phenotyping. 
    
    Input:
        * path to one dicom (other are automatically found.)
        * Patient ID
    
    Output:
        Creates a single nrrd file with the path: $target_path / patient_id + '_ct_scan.nrrd'
    
    """
    target_path = os.path.join(path_to_nrrds, patient_id)
    target_name = os.path.join(target_path, patient_id+"_ct_scan.nrrd")
    os.makedirs(target_path, exist_ok=True)
    cmd_string=r"MitkCLDicom2Nrrd "+\
            "-i \"" + image  + "\"" \
            " -o \"" + target_name + "\""
    print(cmd_string)
    a=subprocess.Popen(cmd_string,shell=True,cwd=path_to_executables)
    a.wait()
    return target_name

def get_spacing_and_origin(file):
    """ Reading nrrd files, extract spacing and origin usign SimpleITK and returning them"""
    image=sitk.ReadImage(file)
    spacing=image.GetSpacing()
    origin=image.GetOrigin()
    return spacing, origin

def create_planarfigure_for_session(session, spacing, origin, patient_id, session_id):
    """
    Given one session of an expert, and the corresponding patient id, the given
    contours are converted into multiple planar figures. 
    Each Nodule gets an ID that is unique for ALL Nodules from all images / reading sessions. 
    
    The planar figures are saved in a path following this structure:
    path_to_planars/<Patient ID>/<Patient_ID>_<Session_ID>_<Nodule_ID>_<ROI_ID>.pf
    
    with the following properties:
    * path_to_planars : Globally specified folder
    * <Patient ID> : Unique Patient ID consisting of patient number and an appendix
    * <Session_ID> : Number of the reading session / expert. Unique to the given patient only.
    * <Nodule ID>  : An globally unique ID of the given Nodule
    * <ROI ID>     : A nodule-wide unique, consecutive number of the current ROI. (Each planar figure contains the annotation of a single slice) 
    """
    # Obtaining the code of the radiologist. Replacing underscore (_) as it is later used to 
    # encode different IDs in the resulting file name.
    radiologist=str(session.find("servicingRadiologistID").text).replace("_","-")
    
    # Reading each Nodule in the given session and creating planar figures for them (if large enough)
    global nodule_id
    for nodule in session.iter('unblindedReadNodule'):
        create_planarfigures_for_nodule(nodule, spacing, origin, patient_id, session_id, radiologist)
        nodule_id = nodule_id + 1

def create_planarfigures_for_nodule(nodule, spacing, origin, patient_id, session_id, radiologist):
    """ 
    Extracts the properties of an given nodule, saves them to the CSV file specified in the
    global variable 'path_to_characteristics' and saves all contours for that 
    nodule as planar figure.
    
    Each contour is given a consecutive number.
    """
    global nodule_id
    nodule_str="{:08n}".format(nodule_id)
    
    # Extract the properties of the nodule
    subtlety=xmlHelper.read_nodule_property(nodule, 'subtlety')
    internalStructure=xmlHelper.read_nodule_property(nodule, 'internalStructure')
    calcification=xmlHelper.read_nodule_property(nodule, 'calcification')
    sphericity=xmlHelper.read_nodule_property(nodule, 'sphericity')
    margin=xmlHelper.read_nodule_property(nodule, 'margin')
    lobulation=xmlHelper.read_nodule_property(nodule, 'lobulation')
    spiculation=xmlHelper.read_nodule_property(nodule, 'spiculation')
    texture=xmlHelper.read_nodule_property(nodule, 'texture')
    malignancy=xmlHelper.read_nodule_property(nodule, 'malignancy')

    # save characteristic and specifics of the nodule to the global CSV-file
    global path_to_characteristics
    with open(path_to_characteristics,"a") as file:
        file.write(";".join([str(patient_id),str(session_id),str(radiologist),str(nodule_str),subtlety,internalStructure,calcification,sphericity,margin,lobulation,spiculation,texture,malignancy])+"\n") 
    
    # Extract all rois necessary specified within the Nodule
    roi_id=0
    for roi in nodule.iter('roi'):
        create_planarfigures_for_roi(roi, spacing, origin, patient_id, session_id, nodule_str, roi_id)
        roi_id=roi_id+1
        
def create_planarfigures_for_roi(roi, spacing, origin, patient_id, session_id, nodule_id, roi_id):
    """ 
    Given the section of XML that specifies a certain ROI, this function creates a 
    planar figure file out of it. 
    
    The planar figure is saved in a path following this structure:
    path_to_planars/<Patient ID>/<Patient_ID>_<Session_ID>_<Nodule_ID>_<ROI_ID>.pf
    
    with the following properties:
    * path_to_planars : Globally specified folder
    * <Patient ID> : Unique Patient ID consisting of patient number and an appendix
    * <Session_ID> : Number of the reading session / expert. Unique to the given patient only.
    * <Nodule ID>  : An globally unique ID of the given Nodule
    * <ROI ID>     : A nodule-wide unique, consecutive number of the current ROI. 
    
    """
    # All Rois are within a single Z-plane, so the z-position needs only to be obtained once
    z_position = roi.find("imageZposition").text
    
    # Create file name and esure that the corresponding folder exists to prevent write errors
    target_path = os.path.join(path_to_planars, patient_id)
    target_name = os.path.join(target_path, patient_id+"_"+str(session_id)+"_"+str(nodule_id)+"_"+str(roi_id)+".pf")
    os.makedirs(target_path, exist_ok=True)
    
    # Convert the given edge information into an XML part describing the planar figure
    vertex_string=""
    edge_id=0
    for edge in roi.iter('edgeMap'):
        x=float(edge[0].text)*spacing[0]
        y=float(edge[1].text)*spacing[1]
        vertex_string=vertex_string+"        <Vertex id=\""+str(edge_id)+"\" x=\""+str(x)+"\" y=\""+str(y)+"\" /> \n"
        edge_id=edge_id+1
    
    # If less than two points are defined, it is not a complete mesh. This happens
    # if the lesion was too small, so the experts didn't draw spacial annotations.
    if edge_id < 2:
        return None
    
    # Read the template, replace the corresponding structures and 
    # save the result as a new planar figure
    with open(planar_template,"r") as file:
        template=file.read()
    template=template.replace("%%origin_z%%", str(z_position))
    template=template.replace("%%origin_x%%", str(origin[0]))
    template=template.replace("%%origin_y%%", str(origin[1]))
    template=template.replace("%%points%%", vertex_string)
    with open(target_name,"w") as file:
        file.write(template)
    
def convert_planar_figures_to_masks(image, patient_id):
    """ Finds all planar figure for a single patient and converts them to segmentations that match the CT of the patient"""    
    for planar_figure in glob.glob(os.path.join(path_to_planars,patient_id,"*.pf")):
        create_mask_for_planar_figure(image, patient_id, planar_figure)
    
def create_mask_for_planar_figure(image, patient_id, planar_figure):
    """ 
    Create a segmentation file from a planar figure, using the corresponding ct file.
    
    All Mask files are saved in a folder with the structure of
    path_to_nrrds/<patient ID>/planar_masks/<Name of the Planar Figure File>.nrrd
    """
    # Create the new filename
    file_name=os.path.basename(planar_figure)
    target_path = os.path.join(path_to_nrrds, patient_id,"planar_masks")
    target_name = os.path.join(target_path, file_name.replace(".pf",".nrrd"))
    os.makedirs(target_path, exist_ok=True)
    
    cmd_string=r"MitkCLPlanarFigureToNrrd "+\
            "-i \"" + image  + "\"" \
            " -p \"" + planar_figure  + "\"" \
            " -o \"" + target_name + "\""
    #print(cmd_string)
    a=subprocess.Popen(cmd_string,shell=True,cwd=path_to_executables)
    a.wait()
    return target_name    
    
def merge_planar_figures_per_nodule(image, patient_id):
    """
    There are two problems associated with the planar figures generated segmentations
    that are based on the way that the original data is presented. First, the 
    segmentations of a each nodes is splitted in multile files, as the corresponding
    ROIS as given as slice-wise contours. Second, corresponding annotations
    of the same nodule are not identified, as lesions share no common id between
    different experts. 
    
    This method tries to match segmentations that are from the same rater and combine
    them. It also tries to identify multiple segmentations of the same nodule by 
    different rater, looking at the overlap of segmentations. 
    
    It is assumed that two segmentations cover the same nodule, if their segmentations
    overlap by more than 10 voxel. 
    
    The new created segmentation has the format
    path_to_nrrds/<Patient ID>/<Patient_ID>_<Session_ID>_<Nodule_ID>_<True Nodule ID>.nii.gz
    with the following properties:
    * path_to_planars : Globally specified folder
    * <Patient ID>       : Unique Patient ID consisting of patient number and an appendix
    * <Session_ID>       : Number of the reading session / expert. Unique to the given patient only.
    * <Nodule ID>        : An globally unique ID of the given Nodule
    * <True Nodule ID>   : A globally minimum unique ID of the nodule. All masks of this nodule should share the same True Nodule ID
    """
    # Loading all masks to numpy arrays and save them in a dictionary. 
    # The keys of the dictionary match the (preliminary) mask id
    origin_path = os.path.join(path_to_nrrds, patient_id,"planar_masks","*.nrrd")
    images={}
    arrays={}
    for mask in glob.glob(origin_path):
        mask_name=os.path.basename(mask)
        mask_limits=mask_name.split("_")
        # The first three properties of the file name (Patient ID, Session ID, and Nodule ID)
        # identify wheter a given ROI belongs to a certain Nodule. (ROI ID is ignored)
        mask_id=mask_limits[0]+"_"+mask_limits[1]+"_"+mask_limits[2]
        # If no array with the mask_id is available, create one
        if mask_id not in images.keys():
            image=sitk.ReadImage(mask)
            images[mask_id]=image
            array=sitk.GetArrayFromImage(image)
            arrays[mask_id]=array
        # If already a planar figure belonging to the given nodule exists, add
        # the new one to the old one (e.g. merge both segmentations)
        else:
            image=sitk.ReadImage(mask)
            array=sitk.GetArrayFromImage(image)
            arrays[mask_id]=arrays[mask_id]+array
    
    for key,idx in zip(images.keys(),range(len(images.keys()))):
        # If values larger than 1 are present in a segmentation, there are 
        # overlaps between two segmentations for this nodule. This should not happen
        # but occures due to errors in the original XML files
        if len(arrays[key][arrays[key]>1])>1:
            write_error("Failed due to wrong segmentations: " + key)
            continue        
        # Identify the smallest global nodule ID for the given nodule. 
        # It is assumed that two segmentations cover the same nodule if more than 
        # 10 voxels are covered by both segmentations. The global nodule id is
        # the smallest nodule id for each nodule
        own_id=int(key.split("_")[2])
        minimum_id=own_id
        for k2 in arrays.keys():
             mask=(arrays[key]*arrays[k2])==1
             if len(arrays[key][mask])>10:
                 new_id=int(k2.split("_")[2])
                 minimum_id=min(minimum_id, new_id)
        #Save the new created segmentation
        minimum_id="{:08n}".format(minimum_id)
        image=sitk.GetImageFromArray(arrays[key])
        image.CopyInformation(images[key])
        key_parts=key.split("_")
        new_key=key_parts[0]+"_"+key_parts[1]+"_"+key_parts[2]+"_"+str(minimum_id)
        sitk.WriteImage(image, os.path.join(path_to_nrrds, patient_id,new_key+".nii.gz"))

def parse_xml_file(file):
    # Create an XML Tree, use own method to remove namespaces 
    root=xmlHelper.create_xml_tree(file)
    
    # Find the Study and Series IDs if possible
    study_uid=xmlHelper.get_study_uid(root)
    series_uid=xmlHelper.get_series_uid(root)
    print(file)
    print(study_uid, series_uid)
    if study_uid is None:
        write_error("Failed to find Study UID: " + file)
        return
    
    # Find the DICOMS matching the study and series ID. 
    # Assuming that all DICOMS to a study/series ID are in one folder. 
    dicom_path, no_of_dicoms=get_dicom_from_study_uid(study_uid, series_uid)
    if no_of_dicoms < 10:
        print(dicom_path)
        print("No DICOM's found for file:",file)
        return
    print(dicom_path)
    # Files are saved in a folder with the structure $PatientID/$StudyID/$SeriesID/$DicomName
    # Removing StudyID, SeriesID and DICOM-Name gives a patient ID
    long_patient_id=os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(dicom_path))))
    patient_id=long_patient_id.replace("LIDC-IDRI-","")
    
    # For some patients, more than one scan is provided (for example due to multiple
    # time points). To ensure that each time point is only scanned one, an appendix
    # is added to the patient_id, ensuring that multiple time points can be selected. 
    for appendix in list_of_appendix:
        target_path = os.path.join(path_to_nrrds, patient_id+appendix)
        if not os.path.exists(target_path):
            patient_id =patient_id+appendix
            print(patient_id)
            break
    
    # Create Nrrd files from DICOMS and reading spacing and orgiin. 
    nrrd_file=create_nrrd_from_dicoms(dicom_path, patient_id)
    spacing, origin = get_spacing_and_origin(nrrd_file)
    
    # Creating multiple planar figures for each reading session. 
    # Each session represents the result of an different expert
    # Each session gets an session ID that is unique for the given patient ID
    # Same session ids for differnt patients do not necessarily correspond to the same expert.
    print("Creating Planar Figure")
    session_id=0
    for session in root.iter('readingSession'):
        create_planarfigure_for_session(session, spacing, origin, patient_id, session_id)
        session_id=session_id+1
    convert_planar_figures_to_masks(nrrd_file, patient_id)
    print("Merging Planar Figures")
    merge_planar_figures_per_nodule(nrrd_file, patient_id)


nodule_id = 0
for xml_file in glob.glob(os.path.join(path_to_xmls,"*","*.xml")):
    global path_to_characteristics
    os.makedirs(os.path.dirname(path_to_characteristics), exist_ok=True)
    with open(path_to_characteristics,"a") as file:
        file.write(";".join(["Patient_ID","Session_ID","Radiologist","Nodule_Str","subtlety","internalStructure","calcification","sphericity","margin","lobulation","spiculation","texture","malignancy"])+"\n") 
    print(xml_file)
    try:
        parse_xml_file(xml_file)
    except:
        write_error("Unspecific error in file : " + xml_file)
    
    