from streamlit.runtime import Runtime
from streamlit.runtime.scriptrunner import add_script_run_ctx


def st_instance_of_type(type_obj: object) -> object:
    import gc
    st_obj = None
    for obj in gc.get_objects():
        if type(obj) is type_obj:
            st_obj = obj
            break
    return st_obj


def get_session_id():
    # st_runtime = st_instance_of_type(Runtime)
    # get session id from the current script runner thread
    session_id = add_script_run_ctx().streamlit_script_run_ctx.session_id
    return session_id
