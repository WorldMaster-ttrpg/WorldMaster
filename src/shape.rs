use std::borrow::Cow;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::to_writer;

/// A 2D vector.
#[pyclass]
#[derive(
    Serialize, Deserialize, Default, Debug, Clone, Copy, Eq, PartialEq, Ord, PartialOrd, Hash,
)]
pub struct Vector2D {
    #[pyo3(get, set)]
    x: i64,

    #[pyo3(get, set)]
    y: i64,
}

/// A 3D vector.
#[pyclass]
#[derive(
    Serialize, Deserialize, Default, Debug, Clone, Copy, Eq, PartialEq, Ord, PartialOrd, Hash,
)]
pub struct Vector3D {
    #[pyo3(get, set)]
    x: i64,

    #[pyo3(get, set)]
    y: i64,

    #[pyo3(get, set)]
    z: i64,
}

#[pyclass]
#[derive(Serialize, Deserialize, Default, Debug, Clone, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub struct Points2D(Vec<Vector2D>);

/// A 2D polygon.  Should always be clockwise.
#[pyclass]
#[derive(Serialize, Deserialize, Default, Debug, Clone, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub struct Polygon2D {
    points: Points2D,
}

/// A base and height.  A polygon base at Z=0 and a height
/// value, to make a prism.
#[pyclass]
#[derive(Serialize, Deserialize, Default, Debug, Clone, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub struct BaseHeight {
    base: Polygon2D,
    height: u64,
}

/// A 3D shape.
/// Will support multiple formats, but currently only supports BaseHeight
#[derive(Serialize, Deserialize, Debug, Clone, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub enum Shape3D {
    BaseHeight(BaseHeight),
}

#[pyclass]
#[derive(Serialize, Deserialize, Debug, Clone, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub struct PyShape3D(Shape3D);

#[pymethods]
impl Vector2D {
    #[new]
    fn py_new(x: i64, y: i64) -> Self {
        Self { x, y }
    }

    fn to_bytes(&self) -> Cow<'static, [u8]> {
        let mut buffer: Cow<'static, [u8]> = Cow::Owned(Vec::with_capacity(32));
        // This shouldn't ever fail.
        postcard::to_io(&self, buffer.to_mut()).unwrap();
        buffer
    }

    #[staticmethod]
    fn from_bytes(bytes: Cow<[u8]>) -> PyResult<Self> {
        postcard::from_bytes(&bytes).map_err(|e| PyValueError::new_err(e.to_string()))
    }

    fn to_json(&self) -> String {
        serde_json::to_string(&self).unwrap()
    }

    #[staticmethod]
    fn from_json(json: &str) -> PyResult<Self> {
        serde_json::from_str(json).map_err(|e| PyValueError::new_err(e.to_string()))
    }

    fn __repr__(&self) -> String {
        let x = self.x;
        let y = self.y;
        format!("<Vector2D({x}, {y})>")
    }
}

pub fn module(_py: Python, module: &PyModule) -> PyResult<()> {
    module.add_class::<Vector2D>();
    module.add_class::<Vector3D>();
    module.add_class::<Points2D>();
    module.add_class::<Polygon2D>();
    module.add_class::<BaseHeight>();
    //module.add_class::<Shape3D>();
    Ok(())
}
