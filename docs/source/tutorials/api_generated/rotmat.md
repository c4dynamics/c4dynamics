# rotmat

## `rotx`

```python
rotx(phi)
```

Generate a 3x3 Direction Cosine Matrix for
a positive rotation about the x-axis by an angle $\varphi$ in radians.

A right-hand rotation matrix about `x` is given by:

$$
R = \begin{bmatrix}
1 & 0 & 0 \\
0 & cos(\varphi) & sin(\varphi) \\
0 & -sin(\varphi) & cos(\varphi)
\end{bmatrix}
$$
### Parameters
phi : float or int
    The angle of rotation in radians.

### Returns
out : numpy.array
    A 3x3 rotation matrix representing the rotation about the x-axis.

### Examples
>>> rotx(0)  # doctest: +NUMPY_FORMAT
[[1  0  0]
 [0  1  0]
 [0  0  1]]

>>> rotx(c4d.pi / 2)  # doctest: +NUMPY_FORMAT
[[1  0  0]
 [0  0  1]
 [0 -1  0]]

>>> v1 = [0, 0, 1]
>>> phi = 90 * c4d.d2r
>>> rotx(phi) @ v1 # doctest: +NUMPY_FORMAT
[0  1  0]

>>> phi = 45 * c4d.d2r
>>> rotx(phi) @ v1 # doctest: +NUMPY_FORMAT
[0  0.707  0.707]

## `roty`

```python
roty(theta)
```

Generate a 3x3 Direction Cosine Matrix for
a positive rotation about the y-axis by an angle $\theta$ in radians.

A right-hand rotation matrix about `y` is given by:

$$
R = \begin{bmatrix}
cos(\theta) & 0& -sin(\theta) \\
0 & 1 & 0 \\
sin(\theta) & 0 & cos(\theta)
\end{bmatrix}
$$
### Parameters
theta : float or int
    The angle of rotation in radians.

### Returns
out : numpy.array
    A 3x3 rotation matrix representing the rotation about the y-axis.

### Examples
>>> roty(0)  # doctest: +NUMPY_FORMAT
[[1  0  0]
 [0  1  0]
 [0  0  1]]

>>> roty(c4d.pi / 2) # doctest: +NUMPY_FORMAT
[[0  0 -1]
 [0  1  0]
 [1  0  0]]

>>> v1 = [0, 0, 1]
>>> phi = 90 * c4d.d2r
>>> roty(phi) @ v1  # doctest: +NUMPY_FORMAT
[-1  0  0]

>>> phi = 45 * c4d.d2r
>>> roty(phi) @ v1 # doctest: +NUMPY_FORMAT
[-0.707  0  0.707]

## `rotz`

```python
rotz(psi)
```

Generate a 3x3 Direction Cosine Matrix for
a positive rotation about the z-axis by an angle $\psi$ in radians.

A right-hand rotation matrix about `z` is given by:

$$
R = \begin{bmatrix}
cos(\psi) & sin(\psi) & 0 \\
-sin(\psi) & cos(\psi) & 0 \\
0 & 0 & 1
\end{bmatrix}
$$
### Parameters
psi : float or int
    The angle of rotation in radians.

### Returns
out : numpy.array
    A 3x3 rotation matrix representing the rotation about the z-axis.

### Examples
>>> rotz(0)  # doctest: +NUMPY_FORMAT
[[1  0  0]
 [0  1  0]
 [0  0  1]]

>>> rotz(c4d.pi / 2)  # doctest: +NUMPY_FORMAT
[[0   1  0]
 [-1  0  0]
 [0   0  1]]

>>> v1 = [0.707, 0.707, 0]
>>> phi = 90 * c4d.d2r
>>> rotz(phi) @ v1 # doctest: +NUMPY_FORMAT
[0.707  -0.707  0]

>>> phi = 45 * c4d.d2r
>>> rotz(phi) @ v1 # doctest: +NUMPY_FORMAT
[1  0  0]

## `dcm321`

```python
dcm321(phi=0.0, theta=0.0, psi=0.0)
```

Generate a 3x3 Direction Cosine Matrix (DCM) for a sequence of
positive rotations around the axes in the following order:
$z$, then $y$, then $x$.

The final form of the matrix is given by:

$$
R = \begin{bmatrix}
c\theta \cdot c\psi
& c\theta \cdot s\psi
& -s\theta \\
s\varphi \cdot s\theta \cdot c\psi - c\varphi \cdot s\psi
& s\varphi \cdot s\theta \cdot s\psi + c\varphi \cdot c\psi
& s\varphi \cdot c\theta \\
c\varphi \cdot s\theta \cdot c\psi + s\varphi \cdot s\psi
& c\varphi \cdot s\theta \cdot s\psi - s\varphi \cdot c\psi
& c\varphi \cdot c\theta
\end{bmatrix}
$$
where

- $c\varphi \equiv cos(\varphi)$
- $s\varphi \equiv sin(\varphi)$
- $c\theta \equiv cos(\theta)$
- $s\theta \equiv sin(\theta)$
- $c\psi \equiv cos(\psi)$
- $s\psi \equiv sin(\psi)$

### Parameters
phi : float or int
    The angle in radian of rotation about `x`, default $\varphi = 0$.
theta : float or int
    The angle in radian of rotation about `y`, default $\theta = 0$.
psi : float or int
    The angle in radian of rotation about `z`, default $\psi = 0$.

### Returns
out : numpy.array
    3x3 Direction Cosine Matrix representing the combined rotation.

### Examples
The inertial velocity vector of an aircraft expressed in an inertial earth frame is given by:

>>> v = [150, 0, 0]

The attitude of the aircraft with respect to the inertial earth frame is
given by the 3 Euler angles:

$$
\phi = 0
\theta = 30 \cdot {\pi \over 180}
\psi = 0
$$
The velocity expressed in body frame:

>>> dcm321(phi = 0, theta = 30 * c4d.d2r, psi = 0) @ v  # doctest: +NUMPY_FORMAT
[129.9  0  75]

## `dcm321euler`

```python
dcm321euler(dcm)
```

Extract Euler angles (roll, pitch, yaw) from a Direction Cosine Matrix (DCM) of 3-2-1 order.

The form of a 3-2-1 rotation matrix:

$$
R = \begin{bmatrix}
c\theta \cdot c\psi
& c\theta \cdot s\psi
& -s\theta \\
s\varphi \cdot s\theta \cdot c\psi - c\varphi \cdot s\psi
& s\varphi \cdot s\theta \cdot s\psi + c\varphi \cdot c\psi
& s\varphi \cdot c\theta \\
c\varphi \cdot s\theta \cdot c\psi + s\varphi \cdot s\psi
& c\varphi \cdot s\theta \cdot s\psi - s\varphi \cdot c\psi
& c\varphi \cdot c\theta
\end{bmatrix}
$$
where

- $c\varphi \equiv cos(\varphi)$
- $s\varphi \equiv sin(\varphi)$
- $c\theta \equiv cos(\theta)$
- $s\theta \equiv sin(\theta)$
- $c\psi \equiv cos(\psi)$
- $s\psi \equiv sin(\psi)$

### Parameters
dcm : numpy.array
    3x3 Direction Cosine Matrix representing a rotation.

### Returns
out : tuple
    A tuple containing Euler angles (roll, pitch, yaw) in degrees.

### Notes
Each set of Euler angles has a geometric singularity where
two angles are not uniquely defined.
It is always the second angle which defines this singular orientation:

- Symmetric Set: 2nd angle is 0 or 180 degrees. For example the 3-1-3 orbit
  angles with zero inclination.
- Asymmetric Set: 2nd angle is ±90 degrees. For example, the 3-2-1 angle of an
  aircraft with 90 degrees pitch.

### Examples
>>> dcm321euler(np.eye(3)) # doctest: +NUMPY_FORMAT
(0, 0, 0)

A rotation matrix that represents the attitude of an aircraft with respect to
an inertial earth frame is given by:

>>> BI = np.array([[ 0.866,     0, -0.5      ]
...                 , [ 0,      1,  0        ]
...                 , [ 0.5,    0,  0.866    ]])
>>> dcm321euler(BI) # doctest: +NUMPY_FORMAT
(0, 30, 0)

## `euler2quat`

```python
euler2quat(phi=0.0, theta=0.0, psi=0.0)
```

Converts 3-2-1 Euler angles to an attitude quaternion.

The quaternion is given in a scalar-first (Hamilton) convention,
$q = [q_w, q_x, q_y, q_z]$, and represents the same
attitude as the DCM of 3-2-1 order, `dcm321`,
i.e. first rotation about the z axis (yaw, $\psi$), then a rotation about the
y axis (pitch, $\theta$), and finally a rotation about the x axis
(roll, $\varphi$):

$$
q_w = c{\varphi \over 2} c{\theta \over 2} c{\psi \over 2}
+ s{\varphi \over 2} s{\theta \over 2} s{\psi \over 2}
q_x = s{\varphi \over 2} c{\theta \over 2} c{\psi \over 2}
- c{\varphi \over 2} s{\theta \over 2} s{\psi \over 2}
q_y = c{\varphi \over 2} s{\theta \over 2} c{\psi \over 2}
+ s{\varphi \over 2} c{\theta \over 2} s{\psi \over 2}
q_z = c{\varphi \over 2} c{\theta \over 2} s{\psi \over 2}
- s{\varphi \over 2} s{\theta \over 2} c{\psi \over 2}
$$
where $c \equiv cos$ and $s \equiv sin$.

### Parameters
phi : float or int
    The angle in radian of rotation about `x`, default $\varphi = 0$.
theta : float or int
    The angle in radian of rotation about `y`, default $\theta = 0$.
psi : float or int
    The angle in radian of rotation about `z`, default $\psi = 0$.

### Returns
out : numpy.ndarray
    A unit quaternion $[q_w, q_x, q_y, q_z]$.

### Examples
```python
>>> import c4dynamics as c4d
>>> c4d.rotmat.euler2quat(0, 0, 0)  # doctest: +NUMPY_FORMAT
[1  0  0  0]
```
A 90 degrees yaw:

```python
>>> c4d.rotmat.euler2quat(psi = 90 * c4d.d2r)  # doctest: +NUMPY_FORMAT
```
  [0.707  0  0  0.707]

## `quat2dcm`

```python
quat2dcm(quat)
```

Returns a Body-from-Reference Direction Cosine Matrix (DCM) of an attitude quaternion.

For a scalar-first unit quaternion $q = [q_w, q_x, q_y, q_z]$,
the DCM is given by:

$$
R = \begin{bmatrix}
1 - 2(q_y^2 + q_z^2)
& 2(q_x q_y + q_w q_z)
& 2(q_x q_z - q_w q_y) \\
2(q_x q_y - q_w q_z)
& 1 - 2(q_x^2 + q_z^2)
& 2(q_y q_z + q_w q_x) \\
2(q_x q_z + q_w q_y)
& 2(q_y q_z - q_w q_x)
& 1 - 2(q_x^2 + q_y^2)
\end{bmatrix}
$$
The result is identical to `dcm321` with the
Euler angles of the same attitude.
The quaternion is normalized before the conversion.

### Parameters
quat : array_like
    A quaternion $[q_w, q_x, q_y, q_z]$.

### Returns
out : numpy.ndarray
    A 3x3 DCM matrix used to rotate a vector
    to the body frame from a reference frame of coordinates.

### Examples
```python
>>> import c4dynamics as c4d
>>> q = c4d.rotmat.euler2quat(theta = 30 * c4d.d2r)
>>> c4d.rotmat.quat2dcm(q) @ [1, 0, 0]  # doctest: +NUMPY_FORMAT
```
  [0.866  0  0.5]

## `quat2euler`

```python
quat2euler(quat)
```

Extracts 3-2-1 Euler angles (roll, pitch, yaw) from an attitude quaternion.

For a scalar-first unit quaternion $q = [q_w, q_x, q_y, q_z]$:

$$
\varphi = atan2(2(q_w q_x + q_y q_z), 1 - 2(q_x^2 + q_y^2))
\theta = asin(2(q_w q_y - q_x q_z))
\psi = atan2(2(q_w q_z + q_x q_y), 1 - 2(q_y^2 + q_z^2))
$$
The quaternion is normalized before the conversion.

### Parameters
quat : array_like
    A quaternion $[q_w, q_x, q_y, q_z]$,
    or an `Nx4` array of `N` quaternions.

### Returns
out : numpy.ndarray
    Euler angles $[\varphi, \theta, \psi]$ in radians,
    or an `Nx3` array of Euler angles for an `Nx4` input.

### Note
The quaternion itself is free of singularities.
The extracted Euler angles, however, are singular
at $\theta = \pm 90°$,
where $\varphi$ and $\psi$ are not uniquely defined
(see `dcm321euler`).

### Examples
```python
>>> import c4dynamics as c4d
>>> q = c4d.rotmat.euler2quat(10 * c4d.d2r, 20 * c4d.d2r, 30 * c4d.d2r)
>>> c4d.rotmat.quat2euler(q) * c4d.r2d  # doctest: +NUMPY_FORMAT
```
  [10  20  30]

