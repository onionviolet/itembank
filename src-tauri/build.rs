fn main() {
    tauri_build::build();
    // Bake the repo root so the dev python sidecar fallback can find
    // itembank.py at runtime (overridable via ITEMBANK_ROOT).
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap_or_else(|| std::path::Path::new("."));
    println!("cargo:rustc-env=ITEMBANK_REPO_ROOT={}", root.display());
}
