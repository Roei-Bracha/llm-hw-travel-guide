import streamlit as st
import queue
import time
from core.engine import TravelGuideEngine
from utils.logger import log_queue

st.set_page_config(
    page_title="Agent-Based Travel Guide",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #31333F;
    }
    .stCard {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #d6d6d6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stStatus {
        font-weight: bold;
        color: #00cc96;
    }
    h1, h2, h3 {
        color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🚗 Agent-Based Travel Guide")
    st.markdown("Generate a multimedia-enriched itinerary for your road trip using AI Agents.")

    # Sidebar Configuration
    with st.sidebar:
        st.header("Configuration")
        start_loc = st.text_input("Start Location", "Times Square, NY")
        end_loc = st.text_input("Destination", "Bryant Park, NY")
        limit = st.number_input("Step Limit (0 for all)", min_value=0, value=3, help="Limit the number of steps to process to save tokens.")
        
        if st.button("Start Journey", type="primary"):
            if not start_loc or not end_loc:
                st.error("Please provide both start and destination.")
            else:
                st.session_state.engine = TravelGuideEngine(start_loc, end_loc, limit if limit > 0 else None)
                st.session_state.engine.start()
                st.session_state.running = True
                st.session_state.logs = []
                st.rerun()

    # Main Area
    if "engine" in st.session_state and st.session_state.running:
        engine = st.session_state.engine
        
        # Status Bar
        progress = engine.get_progress()
        st.progress(progress)
        
        if engine.is_alive():
            st.markdown(f"<p class='stStatus'>Agents are working... ({int(progress*100)}%)</p>", unsafe_allow_html=True)
        else:
            st.session_state.running = False
            st.success("Journey Generation Complete!")
            if engine.error:
                st.error(f"Error: {engine.error}")

        # Real-time Logs (Developer Console)
        with st.expander("👨‍💻 Developer Console (Live Logs)", expanded=True):
            log_container = st.empty()
            
            # Poll log queue
            while not log_queue.empty():
                try:
                    record = log_queue.get_nowait()
                    msg = f"{record.asctime} - {record.name} - {record.levelname} - {record.message}"
                    st.session_state.logs.append(msg)
                except queue.Empty:
                    break
            
            # Display last 20 logs
            log_text = "\n".join(st.session_state.logs[-20:])
            log_container.code(log_text, language="text")
            
        # Auto-refresh while running
        if st.session_state.running:
            time.sleep(1)
            st.rerun()

    # Results Display
    if "engine" in st.session_state and st.session_state.engine.is_complete:
        st.header("Your Itinerary")
        results = st.session_state.engine.results
        
        if not results:
            st.warning("No results generated.")
        
        for i, result in enumerate(results):
            candidate = result.chosen_candidate
            with st.container():
                st.markdown(f"""
                <div class="stCard">
                    <h3>Step {i+1}: {candidate.title}</h3>
                    <p><strong>Type:</strong> {candidate.type.upper()}</p>
                    <p>{candidate.description}</p>
                    <p><em>Judge's Reasoning: {result.judge_reasoning}</em></p>
                    {f'<a href="{candidate.url}" target="_blank">View Content</a>' if candidate.url else ''}
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "running" not in st.session_state:
        st.session_state.running = False
        
    main()
