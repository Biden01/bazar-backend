from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.dependencies import DB, CurrentUser
from app.models.document import VetCert, Invoice
from app.models.user import User
from app.schemas.document import VetCertOut, VetCertCreate, InvoiceOut

router = APIRouter()


@router.get("/vet-certs", response_model=list[VetCertOut])
async def list_vet_certs(user: CurrentUser, db: DB):
    result = await db.execute(select(VetCert).order_by(VetCert.issue_date.desc()))
    certs = result.scalars().all()
    out = []
    for c in certs:
        seller = await db.execute(select(User).where(User.id == c.seller_id))
        seller_user = seller.scalar_one_or_none()
        out.append(VetCertOut(
            id=c.id, number=c.number, product=c.product,
            issue_date=c.issue_date, expiry_date=c.expiry_date,
            issuer=c.issuer, status=c.status,
            seller_name=seller_user.name if seller_user else None,
        ))
    return out


@router.post("/vet-certs", response_model=VetCertOut, status_code=status.HTTP_201_CREATED)
async def create_vet_cert(body: VetCertCreate, user: CurrentUser, db: DB):
    cert = VetCert(seller_id=user.id, **body.model_dump())
    db.add(cert)
    await db.commit()
    await db.refresh(cert)
    return VetCertOut(
        id=cert.id, number=cert.number, product=cert.product,
        issue_date=cert.issue_date, expiry_date=cert.expiry_date,
        issuer=cert.issuer, status=cert.status, seller_name=user.name,
    )


@router.get("/invoices", response_model=list[InvoiceOut])
async def list_invoices(user: CurrentUser, db: DB):
    result = await db.execute(select(Invoice).order_by(Invoice.date.desc()))
    invoices = result.scalars().all()
    out = []
    for inv in invoices:
        seller = await db.execute(select(User).where(User.id == inv.seller_id))
        seller_user = seller.scalar_one_or_none()
        buyer = await db.execute(select(User).where(User.id == inv.buyer_id)) if inv.buyer_id else None
        buyer_user = buyer.scalar_one_or_none() if buyer else None
        out.append(InvoiceOut(
            id=inv.id, number=inv.number, date=inv.date,
            seller_name=seller_user.name if seller_user else None,
            buyer_name=buyer_user.name if buyer_user else None,
            amount=inv.amount, items=inv.item_count, status=inv.status,
        ))
    return out


@router.get("/{doc_id}/download")
async def download_document(doc_id: int, user: CurrentUser, db: DB):
    # Check vet certs first
    result = await db.execute(select(VetCert).where(VetCert.id == doc_id))
    cert = result.scalar_one_or_none()
    if cert and cert.document_url:
        return {"url": cert.document_url}
    raise HTTPException(status_code=404, detail="Document not found")
