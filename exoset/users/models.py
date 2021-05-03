from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, TextField
from django.db import models


#class User(AbstractUser):
#    """Default user for exoset."""

    #: First and last name do not cover name patterns around the globe
#    name = CharField(_("Name of User"), blank=True, max_length=255)
#    first_name = None  # type: ignore
#    last_name = None  # type: ignore

#    def get_absolute_url(self):
#        """Get url for user's detail view.

#        Returns:
#            str: URL for user detail.

#        """
#        return reverse("users:detail", kwargs={"username": self.username})


class User(AbstractUser):

    # fields here should map https://c4science.ch/diffusion/3359/browse/master/conf/LdapDataConnector.conf
    # see detail for epfl https://tequila.epfl.ch/cgi-bin/tequila/serverinfo
    #sciper = CharField(max_length=10, unique=True, null=False, blank=False)
    where = CharField(max_length=200, null=True, blank=True)
    units = TextField(null=True, blank=True)
    classe = CharField(max_length=100, null=True, blank=True)
    statut = CharField(max_length=100, null=True, blank=True)
    group = TextField(null=True, blank=True)
    memberof = TextField(null=True, blank=True)
    sciper = CharField(max_length=10, unique=True, null=True, blank=True)

    def __unicode__(self):
        return """  sciper:    %s
                        username:    %s
                        first_name: %s
                        last_name: %s
                        where:       %s
                        units:       %s
                        group:       %s
                        classe:      %s
                        statut:      %s
                        memberof:    %s
                    """ % (self.username,
                           self.first_name,
                           self.last_name,
                           self.where,
                           self.units,
                           self.group,
                           self.classe,
                           self.statut,
                           self.memberof)


def user_post_save(sender, instance, **kwargs):
    profile, new = User.objects.get_or_create(user=instance)


# Register the trigger
models.signals.post_save.connect(user_post_save, sender=User)

