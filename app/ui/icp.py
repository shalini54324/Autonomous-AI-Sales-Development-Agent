from __future__ import annotations
import streamlit as st
from app.schemas.icp import ICPInput
from app.ui.components import title_block


def render(repo):
    title_block(
        "Ideal Customer Profile (ICP)",
        "Define target firmographics, buyer personas, and product value propositions. This profile drives the AI qualification algorithms and scoring weights.",
        badge_text="TARGETING CRITERIA",
    )
    old = repo.get_icp()

    with st.form("icp_form"):
        # CARD 1: Firmographics
        st.markdown(
            '''
            <div class="form-card-title">
                🏢 1. Target Firmographics & Geometry
            </div>
            ''',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        industry = c1.text_input("Target Industry *", value=old.target_industry if old else "SaaS")
        location = c2.text_input("Target Location / Region *", value=old.target_location if old else "Global")
        c3, c4 = st.columns(2)
        min_e = c3.number_input("Minimum Employees", 1, 100000, value=old.min_employees if old else 50)
        max_e = c4.number_input("Maximum Employees", 1, 100000, value=old.max_employees if old else 500)

        st.markdown("<hr style='border:0; border-top:1px solid #e2e8f0; margin:16px 0;'>", unsafe_allow_html=True)

        # CARD 2: Decision Maker Personas
        st.markdown(
            '''
            <div class="form-card-title">
                👤 2. Target Buyer Personas
            </div>
            ''',
            unsafe_allow_html=True,
        )
        roles = st.text_input(
            "Target Decision-Maker Titles (comma-separated) *",
            value=", ".join(old.target_roles) if old else "CTO, Founder, CEO, Head of Operations",
            help="Roles the agent searches for and identifies within prospect accounts.",
        )

        st.markdown("<hr style='border:0; border-top:1px solid #e2e8f0; margin:16px 0;'>", unsafe_allow_html=True)

        # CARD 3: Product Offering & Value Prop
        st.markdown(
            '''
            <div class="form-card-title">
                💡 3. Product Offering & Ideal Customer Definition
            </div>
            ''',
            unsafe_allow_html=True,
        )
        product = st.text_area(
            "Product / Solution Being Sold *",
            value=old.product_service if old else "AI sales workflow automation platform",
            height=100,
            help="Summary of your product's core capabilities and business outcome.",
        )
        desc = st.text_area(
            "Ideal Customer Narrative *",
            value=old.ideal_customer_description if old else "Growing B2B software teams that want to reduce manual prospecting and improve lead qualification.",
            height=100,
            help="Detailed description of what makes a prospective company a home-run fit.",
        )

        st.markdown("<hr style='border:0; border-top:1px solid #e2e8f0; margin:16px 0;'>", unsafe_allow_html=True)

        # CARD 4: Pain Points & Tech Fit
        st.markdown(
            '''
            <div class="form-card-title">
                ⚡ 4. Pain Points & Technology Requirements
            </div>
            ''',
            unsafe_allow_html=True,
        )
        pains = st.text_area(
            "Known Pain Points (comma-separated)",
            value=", ".join(old.known_pain_points) if old else "repetitive prospecting, inconsistent lead qualification, manual research",
            height=80,
            help="Specific challenges your product solves, used to scan website evidence.",
        )
        tech = st.text_input(
            "Optional Technology Requirements (comma-separated)",
            value=", ".join(old.technology_requirements) if old else "",
            help="e.g. Salesforce, HubSpot, AWS, React (bonus fit score if present).",
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        save = st.form_submit_button("💾 Save ICP Configuration", type="primary")

    if save:
        try:
            icp = ICPInput(
                target_industry=industry,
                target_roles=roles,
                target_location=location,
                min_employees=int(min_e),
                max_employees=int(max_e),
                product_service=product,
                ideal_customer_description=desc,
                known_pain_points=pains,
                technology_requirements=tech,
            )
            repo.save_icp(icp)
            st.success("ICP configuration successfully updated! The intelligence pipeline is calibrated to this profile.")
        except Exception as e:
            st.error(f"Please review the ICP fields: {e}")
