# Tagging model

Every resource created by `spin` is tagged:

| Key        | Value                 | Purpose                         |
|------------|-----------------------|---------------------------------|
| Project    | cloud-starter         | Global scoping                  |
| ManagedBy  | spin                   | Tool that created it            |
| Owner      | <your-handle>         | Accountability / filtering      |
| SpinGroup  | <id>                  | Batch lifecycle / teardown unit |

Teardown (`spin down --group <id> --apply`) operates on **your** resources only (Owner scope) and normally requires a **group**.
