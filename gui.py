"""
Streamlit GUI for CapOptioner
Save this as cap_optioner_gui.py (or any name you like).
Run with:  streamlit run cap_optioner_gui.py -- --memory_dir baseline --debug
"""

import argparse
import streamlit as st
from cap_optioner import CapOptioner


class GUI:
    def __init__(self, agent: CapOptioner = None):
        if agent is None:
            self.agent = CapOptioner(memory_dir="baseline", debug=False) # use default memory_dir and debug
        else:
            self.agent = agent
    # top page
    def render_main(self):
        st.title("🤖 Cap-Optioner Web UI")
        
        st.write(
            """
            **Welcome!**  
            - Select an option from the sidebar to start interacting with the Cap-Optioner agent.
            """
        )
        st.header("Choose an Interaction mode:")
        tab1, tab2, tab3 = st.tabs(["Learn a new skill", "Attempt a task", "Run past example"])
        with tab1:
            # st.header("Learn a new skill")
            self._page_learn_skill()
        with tab2:
            # st.header("Attempt a task")
            self._page_attempt_task()
        with tab3:
            # st.header("Run a past example")
            self._page_run_past_example()


    # ---------------- sub-pages ----------------
    def _page_learn_skill(self):


        # TODO: replace with st components
        if st.button("Start skill parsing"):
            skill = self.agent.skill_parser.parse_skill()
            if skill is None:
                st.warning("Skill parsing aborted.")
                return

            while True:
                self.agent.env_agent.task_setup(gui_mode=True)
                self.agent.attempt_task(skill)
                again = st.radio(
                    "Provide another task to learn this skill?",
                    ["No", "Yes"],
                    horizontal=True,
                    key="learn_again",
                )
                if again == "No":
                    break



    def _page_attempt_task(self):

        self.agent.env_agent.task_setup(gui_mode=True)
        # self.agent.attempt_task()


    def _page_run_past_example(self):

        example_query = st.text_input("Describe a task to search for:", key="example_q")
        if st.button("Search & Run"):
            if not example_query:
                st.error("Please enter a query first.")
                return
            self.agent.run_past_example()


# ----------------------------------------------------------------------
# CLI 入口：支持 --memory_dir 与 --debug
# ----------------------------------------------------------------------
def cli():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--memory_dir", default="baseline")
    # parser.add_argument("--debug", action="store_true")
    # args, _ = parser.parse_known_args()  # Streamlit 会把未识别参数留给我们

    gui_agent = GUI()
    gui_agent.render_main()


if __name__ == "__main__":
    # streamlit run gui.py
    cli()
    