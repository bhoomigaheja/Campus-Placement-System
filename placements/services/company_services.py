from accounts.models import User, CompanyProfile

class CompanyService:
    @staticmethod
    def create_company(email, password, company_name, website='', industry=''):
        if User.objects.filter(email=email).exists():
            raise ValueError("Email already exists.")
            
        user = User.objects.create_user(email=email, password=password, is_company=True)
        company = CompanyProfile.objects.create(
            user=user,
            company_name=company_name,
            website=website,
            industry=industry
        )
        return company

    @staticmethod
    def get_or_create_company_by_name(company_name, creator_user):
        company = CompanyProfile.objects.filter(company_name=company_name).first()
        if not company:
            company = CompanyProfile.objects.create(
                company_name=company_name,
                user=creator_user
            )
        return company
