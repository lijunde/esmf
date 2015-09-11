# $Id$

"""
The Regrid API
"""

#### IMPORT LIBRARIES #########################################################
from ESMF.api.constants import *
from ESMF.interface.cbindings import *
from ESMF.util.decorators import initialize

from ESMF.api.esmpymanager import *
from ESMF.api.grid import *
from ESMF.api.mesh import *
from ESMF.api.field import *

#### Regrid class ##############################################################

class Regrid(object):
    """
    The Regrid object represents a regridding operator between two Fields.  The creation of this object is
    analogous to ESMF_FieldRegridStore(), and calling this object corresponds to ESMF_FieldRegrid().
    ESMF_FieldRegridRelease() is called when the Regrid object goes out of scope (this only happens when the
    Manager goes out of scope, there is a destroy() call for explicit deallocation of the Regrid).

    For more information about the ESMF Regridding functionality, please see the `ESMF Regrid documentation
    <http://www.earthsystemmodeling.org/esmf_releases/public/last/ESMF_refdoc/node5.html#SECTION05012000000000000000>`_.
    """
    # call RegridStore
    @initialize
    def __init__(self, srcfield, dstfield,
                 src_mask_values=None,
                 dst_mask_values=None,
                 regrid_method=None,
                 pole_method=None,
                 regrid_pole_npoints=None,
                 norm_type=None,
                 unmapped_action=None,
                 ignore_degenerate=None,
                 src_frac_field=None,
                 dst_frac_field=None):
        """
        Create a handle to a Regridding operation between two Fields. \n
        Required Arguments: \n
            srcfield: source Field associated with an underlying Grid 
                      or Mesh. \n
            dstfield: destination Field associated with an underlying 
                      Grid or Mesh.  The data in this Field may be 
                      overwritten by this call.\n
        Optional Arguments: \n
            src_mask_values: a numpy array (internally cast to 
                             dtype=numpy.int32)of values that can be 
                             used to specify a masked value on the 
                             source Field. \n
                type: numpy.array \n
                shape: (n, 1) where n is the number of values \n
            dst_mask_values: a numpy array (internally cast to 
                             dtype=numpy.int32)of values that can be 
                             used to specify a masked value on the 
                             destination Field. \n
                type: numpy.array \n
                shape: (n, 1) where n is the number of values \n
            regrid_method: specifies which regridding method to use. \n
                Argument values are: \n
                    (default) RegridMethod.BILINEAR\n
                    RegridMethod.PATCH\n
                    RegridMethod.CONSERVE\n
                    RegridMethod.NEAREST_STOD\n
                    RegridMethod.NEAREST_DTOS\n
            pole_method: specifies which type of artificial pole
                         to construct on the source Grid for regridding.\n
                Argument values are:\n
                    (default for regridmethod == RegridMethod.CONSERVE) PoleMethod.NONE\n
                    (default for regridmethod != RegridMethod.CONSERVE) PoleMethod.ALLAVG\n
                    PoleMethod.NPNTAVG\n
                    PoleMethod.TEETH\n
            regrid_pole_npoints: specifies how many points to average over 
                             if polemethod == PoleMethod.NPNTAVG\n
            norm_type: control which type of normalization to do when generating conservative regridding weights. \n
                Argument values are: \n
                    (default) NormType.DSTAREA \n
                    NormType.FRACAREA \n
            unmapped_action: specifies which action to take if a
                             destination point is found which does not 
                             map to any source point.\n
                Argument values are : \n
                    (default) UnmappedAction.ERROR\n
                    UnmappedAction.IGNORE\n
            ignore_degenerate: Ignore degenerate cells when checking the input
                               Grids or Meshes for errors. If this is set to True,
                               then the regridding proceeds, but degenerate cells
                               will be skipped. If set to False, a degenerate cell
                               produces an error. This currently only applies to
                               RegridMethod.CONSERVE, other regrid methods currently
                               always skip degenerate cells.  The default value is
                               False.\n
            src_frac_field: return a numpy array of values containing 
                            weights corresponding to the amount of 
                            each Field value which contributes to the 
                            total mass of the Field. \n
            dst_frac_field: return a numpy array of values containing 
                            weights corresponding to the amount of each 
                            Field value which contributes to the total 
                            mass of the Field. \n
        Returns: \n
            Regrid \n
        """
        
        # routehandle storage
        self.routehandle = 0

        # type checking
        local_src_mask_values = None
        if src_mask_values is not None:
            if src_mask_values.dtype is not np.int32:
                local_src_mask_values = np.array(src_mask_values, 
                                                 dtype=np.int32)
            else:
                local_src_mask_values = src_mask_values
        # else case handled by initialization to None
        local_dst_mask_values = None
        if dst_mask_values is not None:
            if dst_mask_values.dtype is not np.int32:
                local_dst_mask_values = np.array(dst_mask_values, 
                                                 dtype=np.int32)
            else:
                local_dst_mask_values = dst_mask_values
        # else case handled by initialization to None

        # call into the ctypes layer
        self.routehandle = ESMP_FieldRegridStore(srcfield, dstfield,
                           srcMaskValues=local_src_mask_values,
                           dstMaskValues=local_dst_mask_values,
                           regridmethod=regrid_method,
                           polemethod=pole_method,
                           regridPoleNPnts=regrid_pole_npoints,
                           normType=norm_type,
                           unmappedaction=unmapped_action,
                           ignoreDegenerate=ignore_degenerate,
                           srcFracField=src_frac_field,
                           dstFracField=dst_frac_field)
        
        self._srcfield = srcfield
        self._dstfield = dstfield
        self._src_mask_values = src_mask_values
        self._dst_mask_values = dst_mask_values
        self._regrid_method = regrid_method
        self._pole_method = pole_method
        self._regrid_pole_npoints = regrid_pole_npoints
        self._norm_type = norm_type
        self._unmapped_action = unmapped_action
        self._ignore_degenerate = ignore_degenerate
        self._src_frac_field = src_frac_field
        self._dst_frac_field = dst_frac_field

        # for arbitrary metadata
        self._meta = {}

        # regist with atexit
        import atexit; atexit.register(self.__del__)
        self._finalized = False

    @property
    def srcfield(self):
        return self._srcfield

    @property
    def dstfield(self):
        return self._dstfield

    @property
    def src_mask_values(self):
        return self._src_mask_values

    @property
    def dst_mask_values(self):
        return self._dst_mask_values

    @property
    def regrid_method(self):
        return self._regrid_method

    @property
    def pole_method(self):
        return self._pole_method

    @property
    def regrid_pole_npoints(self):
        return self._regrid_pole_npoints

    @property
    def norm_type(self):
        return self._norm_type

    @property
    def unmapped_action(self):
        return self._unmapped_action

    @property
    def ignore_degenerate(self):
        return self._ignore_degenerate

    @property
    def src_frac_field(self):
        return self._src_frac_field

    @property
    def dst_frac_field(self):
        return self._dst_frac_field

    @property
    def meta(self):
        return self._meta

    @property
    def finalized(self):
        return self._finalized


    def __call__(self, srcfield, dstfield,
                 zero_region=None):
        """
        Call a regridding operation from srcfield to dstfield. \n
        Required Arguments: \n
            srcfield: the Field of source data to regrid. \n
            dstfield: the Field to hold the regridded data. \n
        Optional Arguments: \n
            zero_region: specify which region of the field indices will
                         be zeroed out before adding the values resulting 
                         from the interpolation. \n
                Argument values are: \n
                    (default)TOTAL = the entire Field \n
                    SELECT = only the Field indices which participate 
                             in regridding \n
                    EMPTY = none of the Field \n
        Returns: \n
            dstfield
        """
        # call into the ctypes layer
        ESMP_FieldRegrid(srcfield, dstfield,
                         self.routehandle, zeroregion=zero_region)
        return dstfield

    # manual destructor
    def destroy(self):
        """
        Release the memory associated with a Regrid operation. \n
        Required Arguments: \n
            None \n
        Optional Arguments: \n
            None \n
        Returns: \n
            None \n
        """
        if hasattr(self, '_finalized'):
            if not self._finalized:
                ESMP_FieldRegridRelease(self.routehandle)
                self._finalized = True

    def __del__(self):
        """
        Release the memory associated with a Regrid operation. \n
        Required Arguments: \n
            None \n
        Optional Arguments: \n
            None \n
        Returns: \n
            None \n
        """
        self.destroy()

    def __repr__(self):
        """
        Return a string containing a printable representation of the object
        """
        string = ("Regrid:\n"
                  "    routehandle = %r\n"
                  "    src_mask_values = %r\n"
                  "    dst_mask_values = %r\n"
                  "    regrid_method = %r\n"
                  "    unmapped_action = %r\n"
                  "    src_frac_field = %r\n"
                  "    dst_frac_field = %r\n"
                  "    srcfield = %r\n"
                  "    dstfield = %r\n"
                  %
                  (self.routehandle,
                   self.src_mask_values,
                   self.dst_mask_values,
                   self.regrid_method,
                   self.unmapped_action,
                   self.src_frac_field,
                   self.dst_frac_field,
                   self.srcfield,
                   self.dstfield))

        return string
