# -*- coding: utf-8 -*-
"""funcs related to the package with ca config settings."""

import json

from cadash.inventory.models import Ca

class PackageSupervisor(object):
    """supervises packaging, deployment, listing of settings."""

    @classmethod
    def ca_list_per_vendor(cls, ca_list):
        """returns a dict with pairs (vendor.name_id, <list of CAs>."""
        resp = {}
        for c in ca_list:
            if c.vendor.name_id not in resp:
                resp[c.vendor.name_id] = []
            resp[c.vendor.name_id].append(c)


    @classmethod
    def compile_package(cls, ca_list):
        """generates list of settings for given list of capture agents."""

            settings = {}
            cas = cls.ca_list_per_vendor(ca_list)
            for v, calist in cas.items():
                #TODO: figure out what handler to call
                for ca in calist:
                    s = handler.settings_for(ca)
                except Exception as e:
                    #TODO: handle exception
                    pass
                else:
                    settings[ca.name_id] = s
            return settings

    @classmethod
    def deploy_package(cls, pkg):
        """given pkg, deploys to corresponding CAs."""

        #TODO: figure out what handler to call
        try:
            handle.deploy_list(pkg)
        except Exception as e:
            #TODO: handle exception
            pass
        else:
            return True

    @classmethod
    def create_deploy_package(cls, ca_list):
        """creates and deploy package, based on list of CAs."""
        try:
            pkg = cls.create_and_deploy_list(ca_list)
        except Exception as e:
            #TODO: handle exception
            pass
        else:
            try:
                resp = cls.deploy_package(pkg)
            except Exception as e:
                #TODO: handle exception
                pass
            else:
                return pkg






class DeviceSettingsHandler(object):
    """handler base class for a device specific settings."""

    @classmethod
    def compile_settings_for_ca(cls, ca):
        pass

    @classmethod
    def compile_settings_for_ca_list(cls, ca_list):
        pass


