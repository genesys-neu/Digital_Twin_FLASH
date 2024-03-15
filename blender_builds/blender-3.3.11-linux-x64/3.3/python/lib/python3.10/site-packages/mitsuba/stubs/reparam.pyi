from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload, ModuleType
import mitsuba
import mitsuba as mi

from drjit.router import CustomOp
class _ReparameterizeOp(CustomOp):
    """
        Dr.Jit custom operation that reparameterizes rays based on the paper
    
          "Unbiased Warped-Area Sampling for Differentiable Rendering"
          (Proceedings of SIGGRAPH'20) by Sai Praveen Bangaru,
          Tzu-Mao Li, and Frédo Durand.
    
        This is needed to to avoid bias caused by the discontinuous visibility
        function in gradient-based geometric optimization.
        
    """

    def add_input(self, value):
        """
        
        Register an implicit input dependency of the operation on an AD variable.
        
        This function should be called by the ``eval()`` implementation when an
        operation has a differentiable dependence on an input that is not an
        input argument (e.g. a private instance variable).
        
        Args:
        value (object): variable this operation depends on implicitly.
        
        """
        ...

    def add_output(self, value):
        """
        
        Register an implicit output dependency of the operation on an AD variable.
        
        This function should be called by the
        ef eval() implementation when an
        operation has a differentiable dependence on an output that is not an
        return value of the operation (e.g. a private instance variable).
        
        Args:
        value (object): variable this operation depends on implicitly.
        
        """
        ...

    def backward(self): ...
    def backward_symbolic(self): ...
    def backward_unroll(self): ...
    def eval(self, scene, rng, params, ray, num_rays, kappa, exponent, antithetic, unroll, active): ...
    def forward(self):
        """
        
        Propagate the gradients in the forward direction to 'ray.d' and the
        jacobian determinant 'det'. From a warp field point of view, the
        derivative of 'ray.d' is the warp field direction at 'ray', and
        the derivative of 'det' is the divergence of the warp field at 'ray'.
        
        """
        ...

    def grad_in(self, name):
        """
        
        Access the gradient associated with the input argument ``name`` (fwd. mode AD).
        
        Args:
        name (str): name associated to an input variable (e.g. keyword argument).
        
        Returns:
        object: the gradient value associated with the input argument.
        
        """
        ...

    def grad_out(self):
        """
        
        Access the gradient associated with the output argument (backward mode AD).
        
        Returns:
        object: the gradient value associated with the output argument.
        
        """
        ...

    def name(self): ...
    def set_grad_in(self, name, value):
        """
        
        Accumulate a gradient value into an input argument (backward mode AD).
        
        Args:
        name (str): name associated to the input variable (e.g. keyword argument).
        value (object): gradient value to accumulate.
        
        """
        ...

    def set_grad_out(self, value):
        """
        
        Accumulate a gradient value into the output argument (forward mode AD).
        
        Args:
        value (object): gradient value to accumulate.
        
        """
        ...

    ...

def _sample_warp_field(scene: mitsuba.Scene, sample: mitsuba.Point2f, ray: mitsuba.Ray3f, ray_frame: mitsuba.Frame3f, flip: mitsuba.Bool, kappa: float, exponent: float):
    """
    
    Helper function for reparameterizing rays based on the paper
    
    "Unbiased Warped-Area Sampling for Differentiable Rendering"
    (Procedings of SIGGRAPH'20) by Sai Praveen Bangaru,
    Tzu-Mao Li, and Frédo Durand.
    
    The function is an implementation of the _ReparameterizeOp class below
    (which is in turn an implementation detail of the reparameterize_rays()
    function). It traces a single auxiliary ray and returns an attached 3D
    direction and sample weight. A number of calls to this function are
    generally necessary to reduce the bias of the parameterization to an
    acceptable level.
    
    The function assumes that all inputs are *detached* from the AD graph, with
    one exception: the ray origin (``ray.o``) may have derivative tracking
    enabled, which influences the returned directions. The scene parameter π
    as an implicit input can also have derivative tracking enabled.
    
    It has the following inputs:
    
    Parameter ``scene`` (``mitsuba.Scene``):
    The scene being rendered differentially.
    
    Parameter ``sample`` (``mitsuba.Point2f``):
    A uniformly distributed random variate on the domain [0, 1]^2.
    
    Parameter ``ray`` (``mitsuba.Ray3f``):
    The input ray that should be reparameterized.
    
    Parameter ``ray_frame`` (``mitsuba.Frame3f``):
    A precomputed orthonormal basis with `ray_frame.n = ray.d`.
    
    Parameter ``kappa`` (``float``):
    Kappa parameter of the von Mises Fisher distribution used to
    sample auxiliary rays.
    
    Parameter ``exponent`` (``float``):
    Power exponent applied on the computed harmonic weights.
    
    The function returns a tuple ``(Z, dZ, V, div)`` containing
    
    Return value ``Z`` (``mitsuba.Float``)
    The harmonic weight of the generated sample. (detached)
    
    Return value ``dZ`` (``mitsuba.Vector3f``)
    The gradient of ``Z`` with respect to tangential changes
    in ``ray.d``. (detached)
    
    Return value ``V`` (``mitsuba.Vector3f``)
    The weighted mi.warp field value. Taking the derivative w.r.t.
    scene parameter π gives the vector field that follows an object's
    motion due to π. (attached)
    
    Return value ``div_lhs`` (``mitsuba.Vector3f``)
    Dot product between dZ and the unweighted mi.warp field, which is
    an intermediate value used to compute the divergence of the
    mi.warp field/jacobian determinant of the reparameterization.
    (attached)
    
    """
    ...

def reparameterize_ray(scene: mitsuba.Scene, rng: mitsuba.PCG32, params: mitsuba.SceneParameters, ray: mitsuba.RayDifferential3f, num_rays: int = 4, kappa: float = 100000.0, exponent: float = 3.0, antithetic: bool = False, unroll: bool = False, active: mitsuba.Bool = True) -> Tuple[mitsuba.Vector3f, mitsuba.Float]:
    """
    
    Reparameterize given ray by "attaching" the derivatives of its direction to
    moving geometry in the scene.
    
    Parameter ``scene`` (``mitsuba.Scene``):
    Scene containing all shapes.
    
    Parameter ``rng`` (``mitsuba.PCG32``):
    Random number generator used to sample auxiliary ray directions.
    
    Parameter ``params`` (``mitsuba.SceneParameters``):
    Scene parameters
    
    Parameter ``ray`` (``mitsuba.RayDifferential3f``):
    Ray to be reparameterized
    
    Parameter ``num_rays`` (``int``):
    Number of auxiliary rays to trace when performing the convolution.
    
    Parameter ``kappa`` (``float``):
    Kappa parameter of the von Mises Fisher distribution used to sample the
    auxiliary rays.
    
    Parameter ``exponent`` (``float``):
    Exponent used in the computation of the harmonic weights
    
    Parameter ``antithetic`` (``bool``):
    Should antithetic sampling be enabled to improve convergence?
    (Default: False)
    
    Parameter ``unroll`` (``bool``):
    Should the loop tracing auxiliary rays be unrolled? (Default: False)
    
    Parameter ``active`` (``mitsuba.Bool``):
    Boolean array specifying the active lanes
    
    Returns → (mitsuba.Vector3f, mitsuba.Float):
    Returns the reparameterized ray direction and the Jacobian
    determinant of the change of variables.
    
    """
    ...

