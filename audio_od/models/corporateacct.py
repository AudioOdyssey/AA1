 class corporateacct:
     company_id = 0
     company_name = ""
     company_discount = 0
     has_free_downloads = False
 
  def __init__(self, company_id = 0, company_name="", company_discount=0, has_free_downloads = False):
      self.company_id = company_id
      self.company_name = company_name
      self.company_discount = company_discount
      self.has_free_downloads = has_free_downloads