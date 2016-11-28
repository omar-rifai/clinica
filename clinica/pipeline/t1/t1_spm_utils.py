# import os
# from nipype.interfaces.base import OutputMultiPath, TraitedSpec, isdefined, traits, InputMultiPath, File
# from nipype.interfaces.spm.base import SPMCommand, scans_for_fname, func_is_3d, Info, scans_for_fnames, SPMCommandInputSpec
# from nipype.utils.filemanip import fname_presuffix, filename_to_list, list_to_filename, split_filename

# class DARTELExistingTemplateInputSpec(SPMCommandInputSpec):
#     image_files = traits.List(traits.List(File(exists=True)),
#                               desc="A list of files to be segmented",
#                               field='warp.images', copyfile=False, mandatory=True)
#     template_prefix = traits.Str('Template', usedefault=True,
#                                  field='warp.settings.template',
#                                  desc='Prefix for template')
#     regularization_form = traits.Enum('Linear', 'Membrane', 'Bending',
#                                       field='warp.settings.rform',
#                                       desc='Form of regularization energy term')
#     iteration_parameters = traits.List(traits.Tuple(traits.Range(1, 10),
#                                                     traits.Tuple(traits.Float,
#                                                                  traits.Float,
#                                                                  traits.Float),
#                                                     traits.Enum(1, 2, 4, 8, 16,
#                                                                 32, 64, 128,
#                                                                 256, 512),
#                                                     traits.Enum(0, 0.5, 1, 2, 4,
#                                                                 8, 16, 32)),
#                                        minlen=3,
#                                        maxlen=12,
#                                        field='warp.settings.param',
#                                        desc="""List of tuples for each iteration
#                                        - Inner iterations
#                                        - Regularization parameters
#                                        - Time points for deformation model
#                                        - smoothing parameter
#                                        """)
#     optimization_parameters = traits.Tuple(traits.Float, traits.Range(1, 8),
#                                            traits.Range(1, 8),
#                                            field='warp.settings.optim',
#                                            desc="""Optimization settings a tuple
#                                            - LM regularization
#                                            - cycles of multigrid solver
#                                            - relaxation iterations
#                                            """)
#
#
# class DARTELExistingTemplateOutputSpec(TraitedSpec):
#     final_template_file = File(exists=True, desc='final DARTEL template')
#     template_files = traits.List(File(exists=True), desc='Templates from different stages of iteration')
#     dartel_flow_fields = traits.List(File(exists=True), desc='DARTEL flow fields')
#
#
# class DARTELExistingTemplate(SPMCommand):
#     """Use spm DARTEL to create a template and flow fields
#
#     http://www.fil.ion.ucl.ac.uk/spm/doc/manual.pdf#page=185
#
#     Examples
#     --------
#     >>> import nipype.interfaces.spm as spm
#     >>> dartel = spm.DARTEL()
#     >>> dartel.inputs.image_files = [['rc1s1.nii','rc1s2.nii'],['rc2s1.nii', 'rc2s2.nii']]
#     >>> dartel.run() # doctest: +SKIP
#
#     """
#
#     input_spec = DARTELExistingTemplateInputSpec
#     output_spec = DARTELExistingTemplateOutputSpec
#     _jobtype = 'tools'
#     _jobname = 'dartel'
#
#     def _format_arg(self, opt, spec, val):
#         """Convert input to appropriate format for spm
#         """
#
#         if opt in ['image_files']:
#             return scans_for_fnames(val, keep4d=True, separate_sessions=True)
#         elif opt == 'regularization_form':
#             mapper = {'Linear': 0, 'Membrane': 1, 'Bending': 2}
#             return mapper[val]
#         elif opt == 'iteration_parameters':
#             params = []
#             for param in val:
#                 new_param = {}
#                 new_param['its'] = param[0]
#                 new_param['rparam'] = list(param[1])
#                 new_param['K'] = param[2]
#                 new_param['slam'] = param[3]
#                 params.append(new_param)
#             return params
#         elif opt == 'optimization_parameters':
#             new_param = {}
#             new_param['lmreg'] = val[0]
#             new_param['cyc'] = val[1]
#             new_param['its'] = val[2]
#             return [new_param]
#         else:
#             return super(DARTELExistingTemplate, self)._format_arg(opt, spec, val)
#
#     def _list_outputs(self):
#         outputs = self._outputs().get()
#         outputs['template_files'] = []
#         for i in range(6):
#             outputs['template_files'].append(os.path.realpath('%s_%d.nii' % (self.inputs.template_prefix, i + 1)))
#         outputs['final_template_file'] = os.path.realpath('%s_6.nii' % self.inputs.template_prefix)
#         outputs['dartel_flow_fields'] = []
#         for filename in self.inputs.image_files[0]:
#             pth, base, ext = split_filename(filename)
#             outputs['dartel_flow_fields'].append(os.path.realpath('u_%s_%s%s' % (base,
#                                                                                  self.inputs.template_prefix,
#                                                                                  ext)))
#         return outputs
#

def unzip_nii(in_file):
    from nipype.utils.filemanip import split_filename
    from nipype.algorithms.misc import Gunzip

    _, base, ext = split_filename(in_file)

    # Not compressed
    if ext[-3:].lower() != ".gz":
        print 'no es zip'
        return in_file
    # Compressed
    print 'es_zip'
    gunzip = Gunzip(in_file=in_file)
    gunzip.run()
    return gunzip.aggregate_outputs().out_file


def get_tissue_tuples(tissue_map, tissue_classes, dartel_tissues, save_warped_unmodulated, save_warped_modulated):
    '''
    Method to obtain the list of tuples, one for each tissue class, with the following fields:
         - tissue probability map (4D), 1-based index to frame
         - number of gaussians
         - which maps to save [Native, DARTEL] - a tuple of two boolean values
         - which maps to save [Unmodulated, Modulated] - a tuple of two boolean values

    :param tissue_map: Path to tissue maps
    :param tissue_classes: Classes of images to obtain from segmentation. Ex: [1,2,3] is GM, WM and CSF
    :param dartel_tissues: Classes of images to save for DARTEL template calculation. Ex: [1] is only GM'
    :param save_warped_unmodulated: Save warped unmodulated images for tissues specified in --tissue_classes
    :param save_warped_modulated: Save warped modulated images for tissues specified in --tissue_classes
    :return: List of tuples according to NewSegment input por tissues
    '''

    tissues = []

    for i in range(1, 7):
        n_gaussians = 2

        if i == 4 or i == 5:
            n_gaussians = i - 1

        native_space = False
        dartel_input = False
        warped_unmodulated = False
        warped_modulated = False

        if i in tissue_classes:
            native_space = True
            if save_warped_unmodulated:
                warped_unmodulated = True
            if save_warped_modulated:
                warped_modulated = True

        if i in dartel_tissues:
            dartel_input = True

        tissues.append(((tissue_map, i), n_gaussians, (native_space, dartel_input), (warped_unmodulated, warped_modulated)))

    return tissues


def get_class_images(class_images,index_list):
    """
    utility method to extract class images
    from a multi session class_images set:
    class nb : tissue type
    1 : Grey Matter
    2 : White Matter
    3 : CerebroSpinal Fluid
    4 : Skull
    5 : Out-of-brain soft tissue
    6 : Head surrounding

    :param class_images: image set from which to extract images.
    :param index_list: index list of the classes to extract.
    :return: extracted images in a list of list (without empty lists).

    Example
    -------
    >>> class_n_images = get_class_images(class_images,[1,2])
    """

    # Declare class images list
    class_n_images = {}
    for idx in index_list:
        class_n_images[idx]=[]

    for session in class_images:
        for idx in index_list:
            class_n_images[idx].extend(session[idx-1])

    result = []
    for idx in index_list:
        if class_n_images[idx]:
            result.append(class_n_images[idx])

    return result


def group_nested_images_by_subject(class_images):
    return [[s for tissue in subject for s in tissue] for subject in class_images]


def group_images_list_by_subject(images_list, tissue_classes):
    if len(tissue_classes) == 0:
        return []

    n_tissue_classes = len(tissue_classes)
    n_subjects = len(images_list)/n_tissue_classes
    grouped_images = []

    for subj in range(n_subjects):
        subj_images = []
        for tissue in range(n_tissue_classes):
            subj_images.append(images_list[(tissue * n_subjects) + subj])
        grouped_images.append(subj_images)

    return grouped_images

