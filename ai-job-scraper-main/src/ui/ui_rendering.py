"""UI rendering helpers module.

This module consolidates UI rendering functions from multiple helper modules:
- Company Display Functions: Rendering company information, statistics, and cards
- Job Modal Components: Job modal header, status, description, and action components
- View Mode Selection: View mode selectors and application logic

Provides a unified interface for all UI rendering operations across the application.
"""

from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from src.schemas import Company, Job

# Export all public functions
__all__ = [
    "apply_view_mode",
    "render_action_buttons",
    "render_company_card",
    "render_company_card_with_delete",
    "render_company_card_with_selection",
    "render_company_info",
    "render_company_statistics",
    "render_company_toggle",
    "render_job_description",
    "render_job_header",
    "render_job_status",
    "render_notes_section",
    "select_view_mode",
]


# =============================================================================
# Company Display Functions
# =============================================================================
# =============================================================================
# Company Display Functions
# =============================================================================


def render_company_info(company: dict) -> None:
    """Render company name and URL."""
    st.markdown(f"**{company['name']}**")
    if company.get('url'):
        st.markdown(f"🔗 [{company['url']}]({company['url']})")


def render_company_statistics(company: dict) -> None:
    """Render company scraping statistics and last scraped date."""
    # Display last scraped date
    last_scraped = company.get('last_scraped')
    if last_scraped:
        if hasattr(last_scraped, 'strftime'):
            last_scraped_str = last_scraped.strftime("%Y-%m-%d %H:%M")
        else:
            last_scraped_str = str(last_scraped)
        st.markdown(f"📅 Last scraped: {last_scraped_str}")
    else:
        st.markdown("📅 Never scraped")

    # Display scraping statistics
    scrape_count = company.get('scrape_count', 0)
    if scrape_count > 0:
        success_rate = company.get('success_rate', 1.0)
        success_rate_str = f"{success_rate:.1%}"
        scrape_text = f"📊 Scrapes: {scrape_count} | Success: {success_rate_str}"
        st.markdown(scrape_text)
    else:
        st.markdown("📊 No scraping history")


def render_company_toggle(company: dict, toggle_callback) -> None:
    """Render company active toggle with callback."""
    st.toggle(
        "Active",
        value=company.get('active', True),
        key=f"company_active_{company['id']}",
        help=f"Toggle scraping for {company['name']}",
        on_change=toggle_callback,
        args=(company['id'],),
    )


def render_company_card(company: dict, toggle_callback) -> None:
    """Render a complete company card with info, stats, and toggle."""
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            try:
                render_company_info(company)
            except Exception:
                st.error("Error displaying company info")

        with col2:
            try:
                render_company_statistics(company)
            except Exception:
                st.error("Error displaying company stats")

        with col3:
            try:
                render_company_toggle(company, toggle_callback)
            except Exception:
                st.error("Error displaying company toggle")


def render_company_card_with_delete(
    company: dict,
    toggle_callback,
    delete_callback,
) -> None:
    """Render a company card with info, stats, toggle, and delete button."""
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

        with col1:
            render_company_info(company)

        with col2:
            render_company_statistics(company)

        with col3:
            render_company_toggle(company, toggle_callback)

        with col4:
            company_id = company['id']
            company_name = company['name']
            # Create a unique key for the confirmation checkbox
            confirm_key = f"delete_confirm_{company_id}"

            # Show confirmation checkbox if delete button was clicked
            if st.session_state.get(f"show_delete_confirm_{company_id}", False):
                st.checkbox(
                    "Confirm?",
                    key=confirm_key,
                    help="Check to confirm deletion",
                    on_change=delete_callback,
                    args=(company_id,),
                )
                # Add cancel button
                if st.button("Cancel", key=f"cancel_delete_{company_id}"):
                    st.session_state[f"show_delete_confirm_{company_id}"] = False
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
            # Show delete button
            elif st.button(
                "🗑️ Delete",
                key=f"delete_btn_{company_id}",
                help=f"Delete {company_name} and all associated jobs",
                type="secondary",
            ):
                st.session_state[f"show_delete_confirm_{company_id}"] = True
                st.rerun()


def render_company_card_with_selection(
    company: dict,
    toggle_callback,
    delete_callback,
    selection_callback,
) -> None:
    """Render a company card with selection, info, stats, toggle, and delete."""
    with st.container(border=True):
        col1, col2, col3, col4, col5 = st.columns([0.5, 2.5, 2, 1, 1])

        company_id = company['id']
        company_name = company['name']

        with col1:
            # Selection checkbox
            selected = st.session_state.get("selected_companies", set())
            is_selected = company_id in selected if company_id else False

            st.checkbox(
                f"Select {company_name}",
                value=is_selected,
                key=f"select_company_{company_id}",
                help=f"Select {company_name} for bulk operations",
                on_change=selection_callback,
                args=(company_id,),
                label_visibility="collapsed",
            )

        with col2:
            render_company_info(company)

        with col3:
            render_company_statistics(company)

        with col4:
            render_company_toggle(company, toggle_callback)

        with col5:
            # Create a unique key for the confirmation checkbox
            confirm_key = f"delete_confirm_{company_id}"

            # Show confirmation checkbox if delete button was clicked
            if st.session_state.get(f"show_delete_confirm_{company_id}", False):
                st.checkbox(
                    "Confirm?",
                    key=confirm_key,
                    help="Check to confirm deletion",
                    on_change=delete_callback,
                    args=(company_id,),
                )
                # Add cancel button
                if st.button("Cancel", key=f"cancel_delete_{company_id}"):
                    st.session_state[f"show_delete_confirm_{company_id}"] = False
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
            # Show delete button
            elif st.button(
                "🗑️",
                key=f"delete_btn_{company_id}",
                help=f"Delete {company_name} and all associated jobs",
                type="secondary",
            ):
                st.session_state[f"show_delete_confirm_{company_id}"] = True
                st.rerun()

# =============================================================================
# Job Modal Components
# =============================================================================


def render_job_header(job: "Job") -> None:
    """Render job modal header with title and company info."""
    st.markdown(f"### {job.title}")
    st.markdown(f"**{job.company}** • {job.location}")


def render_job_status(job: "Job") -> None:
    """Render job status and posted date."""
    col1, col2 = st.columns(2)
    with col1:
        if job.posted_date:
            st.markdown(f"**Posted:** {job.posted_date}")
    with col2:
        status_colors = {
            "New": "🔵",
            "Interested": "🟡",
            "Applied": "🟢",
            "Rejected": "🔴",
        }
        icon = status_colors.get(job.application_status, "⚪")
        st.markdown(f"**Status:** {icon} {job.application_status}")


def render_job_description(job: "Job") -> None:
    """Render job description section."""
    st.markdown("---")
    st.markdown("### Job Description")
    st.markdown(job.description)


def render_notes_section(job: "Job") -> str:
    """Render notes section and return the notes value.

    Returns:
        str: Current notes value from text area.
    """
    st.markdown("---")
    st.markdown("### Notes")
    return st.text_area(
        "Your notes about this position",
        value=job.notes or "",
        key=f"modal_notes_{job.id}",
        help="Add your personal notes about this job",
        height=150,
    )


def render_action_buttons(job: "Job", notes_value: str) -> None:
    """Render modal action buttons."""
    from src.ui.utils.job_utils import save_job_notes

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Save Notes", type="primary", use_container_width=True):
            save_job_notes(job.id, notes_value)

    with col2:
        if job.link:
            st.link_button(
                "Apply Now",
                job.link,
                use_container_width=True,
                type="secondary",
            )

    with col3:
        if st.button("Close", use_container_width=True):
            st.session_state.view_job_id = None
            st.rerun()


# =============================================================================
# View Mode Selection
# =============================================================================


def select_view_mode(tab_key: str) -> tuple[str, int | None]:
    """Create view mode selector with responsive, card, and list options.

    Args:
        tab_key: Unique key for the tab to ensure unique widget keys.

    Returns:
        tuple: (view_mode, grid_columns) where view_mode is 'Responsive', 'Card',
               or 'List' and grid_columns is the number of columns for card view or
               None for responsive/list.
    """
    _, menu_col = st.columns([2, 1])

    with menu_col:
        view_mode = st.selectbox(
            "View",
            ["Responsive", "Card", "List"],
            key=f"view_mode_{tab_key}",
            help="Choose how to display jobs - Responsive adapts automatically to device",
            index=0,  # Default to Responsive for best mobile experience
        )

    grid_columns = None
    if view_mode == "Card":
        _, col_selector = st.columns([3, 1])
        with col_selector:
            grid_columns = st.selectbox(
                "Columns",
                [2, 3, 4],
                index=1,  # Default to 3 columns
                key=f"grid_columns_{tab_key}",
                help="Number of columns in card view",
            )

    return view_mode, grid_columns


def apply_view_mode(
    jobs: list,
    view_mode: str,
    grid_columns: int | None = None,
) -> None:
    """Apply the selected view mode to render jobs with responsive support.

    Args:
        jobs: List of jobs to display.
        view_mode: Either 'Card', 'Responsive', or 'List'.
        grid_columns: Number of columns for card view, ignored for responsive/list view.
    """
    from src.ui.components.cards.job_card import (
        render_jobs_grid,
        render_jobs_list,
        render_jobs_responsive_grid,
    )

    if view_mode == "Responsive":
        # Use the new mobile-first responsive grid system
        render_jobs_responsive_grid(jobs)
    elif view_mode == "Card" and grid_columns:
        # Legacy column-based card view
        render_jobs_grid(jobs, num_columns=grid_columns)
    else:
        # List view
        render_jobs_list(jobs)
