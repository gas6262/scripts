"""Import all phase modules to trigger @register_step decorators."""
from platform_cli.steps import (  # noqa: F401
    phase_a_tools,
    phase_b_scaffold,
    phase_c_database,
    phase_d_api,
    phase_e_frontend,
    phase_f_worker,
    phase_g_gcp,
    phase_h_secrets,
    phase_i_cloudbuild,
    phase_j_terraform,
    phase_k_testing,
)
