"""
Pre-indexed database of major Indian Government Welfare Schemes for Tab 3: Scheme Eligibility.
Contains comprehensive scheme definitions, eligibility rules, financial benefits, and documents required.
"""

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
import streamlit as st
from rag_engine import get_embeddings

GOVERNMENT_SCHEMES = [
    {
        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "category": "Agriculture & Farmers",
        "ministry": "Ministry of Agriculture and Farmers Welfare",
        "benefits": "Direct income support of ₹6,000 per year transferred in three equal 4-monthly installments of ₹2,000 into bank accounts via DBT.",
        "eligibility": "Small and marginal landholder farmer families with cultivable landholding up to 2 hectares (now extended to all landholding eligible farmers subject to exclusion criteria). Exclusions: Institutional landholders, constitutional post holders, serving/retired government employees, pensioners receiving > ₹10,000/month, income tax payees.",
        "documents": "Aadhaar Card, Land ownership papers (Khata/Khesra/7/12 extract), Bank Account linked with Aadhaar, Mobile Number.",
        "how_to_apply": "Register online on pmkisan.gov.in or visit the nearest Common Service Centre (CSC) / State Nodal Officer."
    },
    {
        "name": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PM-JAY)",
        "category": "Healthcare & Social Security",
        "ministry": "Ministry of Health and Family Welfare",
        "benefits": "Cashless health insurance coverage up to ₹5,00,000 per family per year for secondary and tertiary care hospitalization across empanelled public and private hospitals.",
        "eligibility": "Families identified on the basis of SECC 2011 (deprivation and occupational criteria in rural/urban areas) and recently expanded to all senior citizens aged 70 years and above irrespective of income.",
        "documents": "Aadhaar Card, Ration Card / Family ID document, Active Mobile Number.",
        "how_to_apply": "Check eligibility on beneficiary.nha.gov.in or visit any empanelled public/private hospital Ayushman Mitra desk."
    },
    {
        "name": "Pradhan Mantri Awas Yojana - Gramin / Urban (PMAY)",
        "category": "Housing & Urban Affairs",
        "ministry": "Ministry of Housing and Urban Affairs / Ministry of Rural Development",
        "benefits": "Financial assistance of ₹1.20 lakh in plain areas and ₹1.30 lakh in hilly/difficult areas for pucca house construction; Credit-linked interest subsidy up to 6.5% for EWS/LIG categories.",
        "eligibility": "Families without a pucca house anywhere in India. Economically Weaker Section (EWS) with annual income up to ₹3,00,000; Low Income Group (LIG) up to ₹6,00,000. Priority for SC/ST, widows, disabled persons.",
        "documents": "Aadhaar Card, Income Certificate, Land ownership / Noc papers, Bank Account Details, Sworn Affidavit of not owning a pucca house.",
        "how_to_apply": "Apply through municipal local body / Gram Panchayat or online via pmaymis.gov.in."
    },
    {
        "name": "Sukanya Samriddhi Yojana (SSY)",
        "category": "Women & Child Development",
        "ministry": "Ministry of Finance",
        "benefits": "High sovereign-guaranteed interest rate (8.2%+ p.a.), compounding annually, with full tax exemption under Section 80C (EEE status). Maturity on 21 years or marriage after age 18.",
        "eligibility": "Parents or legal guardians of a girl child below the age of 10 years. Maximum of 2 accounts per family (exception for triplets/twins). Minimum deposit ₹250/year, maximum ₹1,50,000/year.",
        "documents": "Birth Certificate of girl child, Identity and Address proof of parent/guardian (Aadhaar/PAN/Voter ID), Photographs.",
        "how_to_apply": "Open account at any Post Office branch or authorized commercial bank branch."
    },
    {
        "name": "Pradhan Mantri Mudra Yojana (PMMY)",
        "category": "Micro-Enterprise & Self Employment",
        "ministry": "Ministry of Finance",
        "benefits": "Collateral-free business loans up to ₹20 Lakhs across 3 categories: Shishu (up to ₹50,000), Kishore (₹50,001 to ₹5,00,000), and Tarun (₹5,00,001 to ₹20,00,000).",
        "eligibility": "Any Indian citizen with a business plan for non-farm income generating activity such as manufacturing, processing, trading or service sector.",
        "documents": "Business Plan/Proposal, Identity proof, Address proof, Proof of Business entity registration, 6 months bank statement, Quotation of machinery/items to be purchased.",
        "how_to_apply": "Apply online at udyamimitra.in or submit application to any Commercial Bank, RRB, Small Finance Bank, or MFI."
    },
    {
        "name": "National Social Assistance Programme (NSAP) - Indira Gandhi Old Age Pension",
        "category": "Senior Citizens & Social Welfare",
        "ministry": "Ministry of Rural Development",
        "benefits": "Monthly pension assistance ranging from ₹200 to ₹1,000+ (augmented by state government top-ups, often reaching ₹1,500 - ₹3,000/month).",
        "eligibility": "Persons aged 60 years and above living Below Poverty Line (BPL) as per central/state BPL criteria.",
        "documents": "Age proof (Aadhaar / Voter ID / Birth Certificate), BPL Card / Ration Card, Bank / Post office account details.",
        "how_to_apply": "Apply through the Block Development Office (BDO), Municipal Corporation, or State Social Welfare Portal (nsap.nic.in)."
    },
    {
        "name": "PM SVANidhi (Street Vendor's AtmaNirbhar Nidhi)",
        "category": "Urban Livelihoods",
        "ministry": "Ministry of Housing and Urban Affairs",
        "benefits": "Collateral-free working capital loan of ₹10,000 (1st tranche), ₹20,000 (2nd tranche), and ₹50,000 (3rd tranche) with 7% interest subsidy on timely repayment and digital cashback.",
        "eligibility": "Street vendors and hawkers vending in urban areas on or before March 24, 2020 holding a Certificate of Vending or Identity Card issued by Urban Local Body (ULB).",
        "documents": "Vending Card / Letter of Recommendation (LoR) from ULB, Aadhaar Card, Bank Account linked to mobile.",
        "how_to_apply": "Apply via pmsvanidhi.mohua.gov.in or through Urban Local Bodies / CSC centers."
    },
    {
        "name": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
        "category": "Maternal & Child Health",
        "ministry": "Ministry of Women and Child Development",
        "benefits": "Maternity cash incentive of ₹5,000 for first child in two installments and ₹6,000 for second child if girl child to compensate for wage loss and promote nutritional well-being.",
        "eligibility": "Pregnant Women and Lactating Mothers (PW&LM) aged 19 years and above for first two live births. Excludes regular government employees.",
        "documents": "Mother and Child Protection (MCP) Card, Aadhaar Cards of husband and wife, Bank account details linked to Aadhaar.",
        "how_to_apply": "Register at nearest Anganwadi Centre (AWC) or approved health facility or online via pmmvy.wcd.gov.in."
    },
    {
        "name": "Stand-Up India Scheme",
        "category": "Entrepreneurship (SC/ST & Women)",
        "ministry": "Ministry of Finance",
        "benefits": "Bank loans between ₹10 Lakhs and ₹1 Crore to at least one SC or ST borrower and at least one woman borrower per bank branch for setting up greenfield enterprises.",
        "eligibility": "SC/ST and/or woman entrepreneurs above 18 years of age setting up non-farm greenfield manufacturing, service, agri-allied, or trading ventures.",
        "documents": "Project report, Identity & Address proofs, Caste certificate (if applicable), Balance sheets, PAN card, Pollution clearances if relevant.",
        "how_to_apply": "Apply online at standupmitra.in or directly at commercial bank branches."
    },
    {
        "name": "PM Vishwakarma Scheme",
        "category": "Artisans & Traditional Craftspeople",
        "ministry": "Ministry of Micro, Small and Medium Enterprises",
        "benefits": "Recognition via PM Vishwakarma Certificate and ID Card, skill training with ₹500/day stipend, toolkit incentive of ₹15,000, and collateral-free credit support up to ₹3,00,000 at concessional 5% interest rate.",
        "eligibility": "Traditional artisans working in 18 identified trades (e.g. Carpenter, Blacksmith, Sculptor, Goldsmith, Potter, Cobbler, Tailor, Barber, Mason) with hands-and-tools work in unorganized sector.",
        "documents": "Aadhaar Card, Mobile Number, Bank details, Ration card, Trade details.",
        "how_to_apply": "Free registration through Common Services Centres (CSC) with biometric verification on pmvishwakarma.gov.in."
    }
]


def get_schemes_as_documents() -> list[Document]:
    """
    Format scheme records into structured LangChain Document objects for embedding into FAISS.
    """
    documents = []
    for s in GOVERNMENT_SCHEMES:
        content = f"""Scheme Name: {s['name']}
Category: {s['category']}
Ministry: {s['ministry']}
Benefits: {s['benefits']}
Eligibility Criteria: {s['eligibility']}
Required Documents: {s['documents']}
Application Procedure: {s['how_to_apply']}"""

        doc = Document(
            page_content=content,
            metadata={
                "name": s["name"],
                "category": s["category"],
                "ministry": s["ministry"],
                "source": "Government Welfare Database"
            }
        )
        documents.append(doc)
    return documents


_SCHEMES_VECTORSTORE = None


def get_schemes_vectorstore() -> FAISS:
    """
    Create and cache a FAISS vector store containing all government welfare schemes.
    """
    global _SCHEMES_VECTORSTORE
    if _SCHEMES_VECTORSTORE is not None:
        return _SCHEMES_VECTORSTORE

    docs = get_schemes_as_documents()
    embeddings = get_embeddings()
    _SCHEMES_VECTORSTORE = FAISS.from_documents(docs, embeddings)
    return _SCHEMES_VECTORSTORE
