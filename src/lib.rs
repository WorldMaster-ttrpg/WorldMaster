use pyo3::prelude::*;

pub mod shape;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "_worldmaster_rust")]
fn _worldmaster_rust(py: Python, m: &PyModule) -> PyResult<()> {
    let shape = shape::register(py, m)?;
    m.add("shape", shape)?;
    py.import("sys")?
        .getattr("modules")?
        .set_item("worldmaster.shape", shape)?;
    Ok(())
}
