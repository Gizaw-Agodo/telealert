from typing import Sequence
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db_session
from app.models.channel import Channel
from app.models.rule import AlertRule
from app.models.user import User
from app.schemas.rule import AlertRuleCreate, AlertRuleResponse, AlertRuleUpdate

from telethon.tl.functions.channels import JoinChannelRequest # type: ignore
from telethon.errors import ChannelPrivateError, FloodWaitError # type: ignore
from app.workers.telethon_collector import client as telethon_client

router = APIRouter(prefix="/rules", tags=["Alert Rules"])


@router.post("/", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    rule_in: AlertRuleCreate, db: AsyncSession = Depends(get_db_session)
) -> AlertRule:
    # 1. Verify User exists
    result = await db.execute(select(User).where(User.id == rule_in.user_id))
    user: User | None = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # 2. Enforce active rule quotas
    rules_count_result = await db.execute(
        select(func.count(AlertRule.id)).where(
            AlertRule.user_id == user.id, AlertRule.is_active == True
        )
    )

    active_rules_count: int = rules_count_result.scalar_one() or 0
    if active_rules_count >= user.max_active_rules:
        raise HTTPException(
            status_code=400,
            detail=f"Rule limit reached. Maximum allowed: {user.max_active_rules}"
        )

    # 3. Clean up the channel username (remove '@' and lower)
    clean_username = rule_in.channel_username.replace("@", "").strip().lower()

    # 4. Check if channel exists, if not, create it
    channel_result = await db.execute( select(Channel).where(Channel.username == clean_username) )
    channel: Channel | None = channel_result.scalar_one_or_none()

    if not channel:
        try:
            await telethon_client(JoinChannelRequest(clean_username)) # type: ignore
            
        except ChannelPrivateError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Cannot join this channel because it is private."
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="This channel does not exist or the username is invalid."
            )
        except FloodWaitError as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
                detail=f"Telegram rate limit reached. Please try again in {e.seconds} seconds."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Failed to join channel: {str(e)}"
            )

        channel = Channel(username=clean_username, is_joined=True)
        db.add(channel)
        await db.commit()
        await db.refresh(channel)

    # 5. Create the Rule
    new_rule = AlertRule(
        user_id=user.id,
        channel_id=channel.id,
        keyword=rule_in.keyword,
        match_type=rule_in.match_type,
        is_case_sensitive=rule_in.is_case_sensitive,
    )
    db.add(new_rule)
    await db.commit()
    
    # Refresh and load the relationship for the response
    await db.refresh(new_rule)
    result_with_rel = await db.execute(
        select(AlertRule)
        .options(selectinload(AlertRule.channel))
        .where(AlertRule.id == new_rule.id)
    )
    return result_with_rel.scalar_one()


@router.get("/user/{user_id}", response_model=list[AlertRuleResponse])
async def get_user_rules(user_id: str, db: AsyncSession = Depends(get_db_session)) -> Sequence[AlertRule]:
    result = await db.execute(
        select(AlertRule)
        .options(selectinload(AlertRule.channel))
        .where(AlertRule.user_id == user_id, AlertRule.deleted_at.is_(None))
    )
    return result.scalars().all()


@router.patch("/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: str, rule_update: AlertRuleUpdate, db: AsyncSession = Depends(get_db_session)
) -> AlertRule:
    result = await db.execute(
        select(AlertRule)
        .options(selectinload(AlertRule.channel))
        .where(AlertRule.id == rule_id)
    )
    rule: AlertRule | None = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found.")

    # Update provided fields
    update_data = rule_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)

    await db.commit()
    await db.refresh(rule)
    return rule