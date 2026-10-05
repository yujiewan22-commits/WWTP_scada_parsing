from app.db.base import Base
from app.db.session import (
    engine,
    SessionLocal,
)

from app.models import Organization


# ============================================================
# Organization 基础数据维护入口
#
# 后续如需：
# 1. 新增组织
# 2. 修改组织名称
#
# 统一在这里维护。
#
# 注意：
# - code 是业务唯一编码，原则上不要随意修改。
# - name 可以正常调整。
# - 修改后重新执行：
#
#   python seed_demo.py
#
# 即可同步到数据库。
# ============================================================

ORGANIZATIONS = [
    {
        "code": "LJ",
        "name": "龙江分部",
    },
    {
        "code": "SD",
        "name": "山东分部",
    },
    {
        "code": "WH",
        "name": "武汉分部",
    },
    {
        "code": "FD",
        "name": "复旦分部",
    },
    {
        "code": "NF",
        "name": "南方分部",
    },
    {
        "code": "LX",
        "name": "联熹分部",
    },
    {
        "code": "BJ",
        "name": "宝金刚",
    },
]


# ============================================================
# 同步 Organization 基础数据
#
# 规则：
# 1. code 不存在 -> 新增
# 2. code 已存在 -> 更新 name
# 3. 不删除数据库中其他业务数据
# ============================================================

def seed_organizations(
    db,
):
    for item in ORGANIZATIONS:

        organization = (
            db.query(Organization)
            .filter(
                Organization.code
                == item["code"]
            )
            .first()
        )

        # ----------------------------------------------------
        # 已存在：
        # 更新组织名称
        # ----------------------------------------------------

        if organization:
            organization.name = item["name"]

            print(
                f"更新组织："
                f"{item['code']} "
                f"{item['name']}"
            )

        # ----------------------------------------------------
        # 不存在：
        # 新增组织
        # ----------------------------------------------------

        else:
            organization = Organization(
                code=item["code"],
                name=item["name"],
            )

            db.add(organization)

            print(
                f"新增组织："
                f"{item['code']} "
                f"{item['name']}"
            )

    db.commit()


# ============================================================
# 主程序
# ============================================================

def main():
    # 创建不存在的数据表
    #
    # 注意：
    # create_all 不会删除已有表和已有数据。
    Base.metadata.create_all(
        bind=engine
    )

    db = SessionLocal()

    try:
        seed_organizations(db)

        print()
        print(
            "Organization 基础数据同步完成"
        )

        print()
        print(
            "当前组织列表："
        )

        organizations = (
            db.query(Organization)
            .order_by(
                Organization.id
            )
            .all()
        )

        for organization in organizations:
            print(
                f"id={organization.id}, "
                f"code={organization.code}, "
                f"name={organization.name}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()