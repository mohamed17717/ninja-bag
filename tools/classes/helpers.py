import user_agents


def ua_details(ua):
  user_agent = user_agents.parse(ua)
  return {
    'ua': str(user_agent),

    'browser': {
      'family': user_agent.browser.family,
      'version': user_agent.browser.version,
      'version_string': user_agent.browser.version_string,
    },

    'os': {
      'family': user_agent.os.family,
      'version': user_agent.os.version,
      'version_string': user_agent.os.version_string,
    },

    'device': {
      'family': user_agent.device.family,
      'brand': user_agent.device.brand,
      'model': user_agent.device.model,
    },

    'flags': {
      'is_mobile': user_agent.is_mobile,
      'is_tablet': user_agent.is_tablet,
      'is_touch_capable': user_agent.is_touch_capable,
      'is_pc': user_agent.is_pc,
      'is_bot': user_agent.is_bot,
    }
  }
