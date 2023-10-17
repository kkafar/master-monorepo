---
State for 17.10.2023
---

# How to use the solver

1. Clone ecrs repo & checkin

```
git clone https://github.com/ecrs-org/ecrs.git ecrs && cd ecrs
```

2. Compile the solver

```
cargo build --example jssp --release
```

3. Run it 

```
cargo run --example jssp --release -- --input-file <input_file> --output-dir <output_dir>
```

or run the binary directly:

```
target/release/examples/jssp 
```

Checkout 

## Copy-paste friendly section

```
git clone https://github.com/ecrs-org/ecrs.git ecrs && cd ecrs
cargo build --example jssp --release
```

# How does the solver work





## How does 

The solver is based on classic genetic algorithms

