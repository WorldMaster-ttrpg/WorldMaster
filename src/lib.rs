use pyo3::prelude::*;

pub mod shape;

/// Create and register a submodule in the parent madule, and set it up in
/// sys.modules.
macro_rules! submodule {
    ($python:ident, $parent:ident, $path:literal, $register:path) => {{
        fn setup<F>(
            py: ::pyo3::marker::Python,
            m: &::pyo3::types::PyModule,
            path: &str,
            register: F,
        ) -> PyResult<()>
        where
            for<'a> F: Fn(Python<'a>, &'a PyModule) -> PyResult<()>,
        {
            let last = path.split('.').rev().next().unwrap();
            let module = PyModule::new(py, path)?;
            register(py, module)?;
            m.add(last, module)?;
            py.import("sys")?
                .getattr("modules")?
                .set_item($path, module)?;
            Ok(())
        }
        setup($python, $parent, $path, $register)
    }};
}

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "_worldmaster_rust")]
fn _worldmaster_rust(py: Python, m: &PyModule) -> PyResult<()> {
    submodule!(py, m, "worldmaster.shape", shape::module)?;
    Ok(())
}
