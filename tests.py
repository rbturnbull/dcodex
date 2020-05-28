from django.test import TestCase

from .models import *

# Create your tests here.
class FamilyTests(TestCase):
    def test_affiliation_all(self):
        """
        manuscript.families_at( verse ) returns the family for any verse when there is a AffiliationAll()
        """
        ms = Manuscript(name="Test Manuscript")
        ms.save()        
        family = Family(name="Test Family 1")
        family.save()
        family2 = Family(name="Test Family 2")
        family2.save()

        verse = Verse(rank=1)
        verse.save()        
        family.add_manuscript_all( ms )

        self.assertIs( ms.families_at(verse).count(), 1 )
        self.assertTrue( ms.is_in_family_at(family, verse) )
        self.assertFalse( ms.is_in_family_at(family2, verse) )        
    
    def test_affiliation_range(self):
        """
        manuscript.families_at( verse ) returns the family for any verse a range
        """
        
        ms = Manuscript(name="Test Manuscript")
        ms.save()        
        family = Family(name="Test Family 1")
        family.save()
        family2 = Family(name="Test Family 2")
        family2.save()

        verses = [Verse(rank=i+1) for i in range(10)]
        for verse in verses:
            verse.save()
            
        affiliation = family.add_manuscript_range( ms, start_verse=verses[1], end_verse=verses[5] )
        
        gold_values = [False,True,True,True,True,True,False,False,False,False]        
        
        for verse, gold in zip( verses, gold_values ):
            self.assertIs( ms.is_in_family_at(family, verse), gold )
        
    def test_affiliation_overlap(self):
        """
        Tests the ability for families to overlap.
        """
        
        ms1 = Manuscript(name="Test Manuscript 1")
        ms1.save()        
        ms2 = Manuscript(name="Test Manuscript 2")
        ms2.save()        
        family1 = Family(name="Test Family 1")
        family1.save()
        family2 = Family(name="Test Family 2")
        family2.save()

        verses = [Verse(rank=rank) for rank in range(10)]
        for verse in verses:
            verse.save()
            
        family2.add_manuscript_all( ms1 )
        family2.add_manuscript_range( ms2, start_verse=verses[1], end_verse=verses[5] )
        
        family1.add_affiliated_family_range( family2, start_verse=verses[3], end_verse=verses[8] )
        
        print( "family2.manuscript_ids_at( verses[3] )", family2.manuscript_ids_at( verses[3] ) )
        
        print("LOOOOOK")
        print( "family1.manuscript_ids_at( verses[3] )", family1.manuscript_ids_at( verses[3] ) )
        print( "family1.manuscript_ids_at( verses[3] )", family1.manuscript_ids_at( verses[3] ) )
        print( "ms1.family_ids_at( verses[3] )", ms1.family_ids_at( verses[3] ) )
        print( "ms2.family_ids_at( verses[3] )", ms2.family_ids_at( verses[3] ) )
             
        
        self.assertEquals( ms1.is_in_family_at(family1, verses[0]), False )
        self.assertEquals( ms2.is_in_family_at(family1, verses[0]), False )
        self.assertEquals( ms1.is_in_family_at(family1, verses[1]), False )
        self.assertEquals( ms2.is_in_family_at(family1, verses[1]), False )
        self.assertEquals( ms1.is_in_family_at(family1, verses[2]), False )
        self.assertEquals( ms2.is_in_family_at(family1, verses[2]), False )
        self.assertEquals( ms1.is_in_family_at(family1, verses[3]), True  )
        self.assertEquals( ms2.is_in_family_at(family1, verses[3]), True  )
        self.assertEquals( ms1.is_in_family_at(family1, verses[4]), True  )
        self.assertEquals( ms2.is_in_family_at(family1, verses[4]), True  )
        self.assertEquals( ms1.is_in_family_at(family1, verses[5]), True  )
        self.assertEquals( ms2.is_in_family_at(family1, verses[5]), True  )
        self.assertEquals( ms1.is_in_family_at(family1, verses[6]), True  )
        self.assertEquals( ms2.is_in_family_at(family1, verses[6]), False )
        self.assertEquals( ms1.is_in_family_at(family1, verses[7]), True  )
        self.assertEquals( ms2.is_in_family_at(family1, verses[7]), False )
        self.assertEquals( ms1.is_in_family_at(family1, verses[8]), True  )
        self.assertEquals( ms2.is_in_family_at(family1, verses[8]), False )
        self.assertEquals( ms1.is_in_family_at(family1, verses[9]), False )
        self.assertEquals( ms2.is_in_family_at(family1, verses[9]), False )
