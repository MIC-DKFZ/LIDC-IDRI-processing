 LIDC Data processing scripts
 ============================
 
The scripts within this repository can be used to convert the LIDC-IDRI data. After calling this script,
the image and segmentation data is available in nifti/nrrd format and the nodule characteristics are available 
in a single comma separated (csv) file.

## Requirements
The scripts uses some standard python libraries (glob, os, subprocess, numpy, and xml), the python library SimpleITK. 
Additionally, some command line tools from MITK are used. They can be either obtained by building MITK and enabling 
the classification module or by installing [MITK Phenotyping][http://http://mitk.org/Phenotyping] which contains all 
necessary command line tools. 

## Basic Usage
 * Download the data from the [LIDC-IDRI][https://wiki.cancerimagingarchive.net/display/Public/LIDC-IDRI] website. Required are the Image DICOM files and the the describing XML files (Radiologist Annotations/Segmentations (XML format)). 
 * If not already happend, build or download and install [MITK Phenotyping][http://http://mitk.org/Phenotyping]
 * Adapt the paths in the file "lidc_data_to_nifti.py"
 * Run the script "lidc_data_to_nifti.py"
 
Following input paths needs to be defined: 
 * path_to_executables : Path where the command line tool from MITK Phenotyping can be found
 * path_to_dicoms : Folder which contains the DICOM image files (not the segmentation dicoms)
 * path_to_xmls : Folder that contains the XML which describes the nodules
Following output paths needs to be defined: 
 * path_to_nrrds : Folder that will contain the created Nrrd / Nifti Files
 * path_to_planars :Folder that will contain the Planar figure for each subject
 * path_to_characteristics : Path to a CSV File, where the characteristic of a nodule will be stored. If the file exists, the new content will be appended. 
 * path_to_error_file : Path to an error file where error messages are written to. Existing files will be appended.

## Output / Result

The output created of this script consists of Nrrd-Files containing a whole DICOM Series (i.e. an 
complete 3D CT image), Nifti (.nii.gz) files of the Nodule-Segmentations (3D), Nrrd and Planar 
Figures (.pf) containing slice-wise segmentations of Nodules.

The data are stored in subfolders, indicating the <Patient ID>. The 5 sign <Patient ID> matches the 
numerical part of the Patient ID that is used in the LIDC_IDRI Dicom folder. However, since 
some patients come with more than one CT image, the <Patient ID> is appended a single letter,
so that each CT scan has an unique <Patient ID>. For example, the folder "LIDC_IDRI-0129" may contain 
two CT images, which will then have the <Patient ID> "0129a" and "0129b".

There are up to four reader sessions given for each patient and image. <Session ID> is a 1-sign number indicating 
the rang of expert FOR THE GIVEN IMAGE. According to the corresponding publication, each session 
was done by one of 12 experts. However, it is not possible to ensure that two images where 
annotated by the same expert. Therefore, two images might be annotated by different experts even 
if they have the same <Session ID>

Each combination of Nodule and Expert has an unique 8-digit <Nodule ID>, for example 0000358. This ID is unique between all
created segmentations of nodules and experts. This means that two segmentations of the 
same Nodule will have different <Nodule ID>s. In contrast to this, the 8-digit <True Nodule ID> is the 
same for all segmentations of the same nodule. It is defined as the minimum <Nodule ID> of all 
segmentations of a given Nodule.

The <ROI ID> is an id, which is unique within a set of Planar Figures or 2D Segmentations 
of a single nodule. It is used to differenciate multiple planes of segmentations of the same object.
 
Based on these definitions, the following files are created:
 * path_to_nrrds/<Patient ID>/<Patient_ID>_ct_scan.nrrd : A nrrd file containing the 3D ct image
 * path_to_nrrds/<Patient ID>/<Patient_ID>_<Session ID>_<Nodule ID>_<True Nodule ID>.nii.gz : Nifti files containing the segmentation of nodules
 * path_to_nrrds/<Patient ID>/planar_masks/<Patient_ID>_<Session ID>_<Nodule ID>_<ROI ID>.nrrd : Nrrd-Files containing a single plane of the Nodule Segmentations
 * path_to_planars/<Patient ID>/<Patient_ID>_<Session ID>_<Nodule ID>_<ROI ID>.pf : Planar Figure-Files containing a single plane of the Nodule Segmentations

In addition, the characteristic of the nodules are saved in the file specified in path_to_characteristics
and errors occuring during the whole process are recorded in path_to_error_file
 
## Limitations
The script had been developed using windows. It should be possible to execute it using linux, however this had never
been tested. Problems may be caused by the subprocess calls (calling the executables of MITK Phenotyping).

Also, the script had been developed for own research and is not extensivly tested. It is possible that i faulty included
some limitations. 

I've deloped this script when there were no DICOM Seg-files for the LIDC_IDRI available online. 
So this script relys on the XML-description, which might not be the best solution. Feel free to extend
/ write a new solution which makes use of the now available DICOM Seg objects.

## Further questions
If you have suggestions or questions, you can reach me (Michael Goetz) at m.goetz@dkfz-heidelberg.de

## Licence

Copyright (c) 2003-2019 German Cancer Research Center,
Division of Medical Image Computing
All rights reserved.

Redistribution and use in source and binary forms, with or
without modification, are permitted provided that the
following conditions are met:

 * Redistributions of source code must retain the above
   copyright notice, this list of conditions and the
   following disclaimer.

 * Redistributions in binary form must reproduce the above
   copyright notice, this list of conditions and the
   following disclaimer in the documentation and/or other
   materials provided with the distribution.

 * Neither the name of the German Cancer Research Center,
   nor the names of its contributors may be used to endorse
   or promote products derived from this software without
   specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.


