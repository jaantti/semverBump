#ifndef THEMISPP_LIB_VEHICLE_CONFIGURATION_HPP
#define THEMISPP_LIB_VEHICLE_CONFIGURATION_HPP

#include <sstream>
#include <string>

namespace themis {
  // major, minor, patch, 0-release, 1-test
  const int version[8] = {1, 2, 0, 0};

  /*!
   * Returns THeMIS++ version.
   * Version has two formats:
   *  - X.Y.Z - release version
   *  - X.Y.Z-test - test or debug version
   * @return
   */
  inline std::string getVersion() {
    std::stringstream ss;
    ss << "Version: " << themis::version[0] << "." << themis::version[1]
       << "." << themis::version[2] << (themis::version[3] == 1 ? "-test" : "");
    return ss.str();
  }

  namespace udp {
    const uint16_t BUFFER_SIZE = 2014;
  }

  namespace hardware {
    namespace fan {
      constexpr uint8_t FAN_COUNT = 5;
    }
  }
}

#endif //THEMISPP_LIB_VEHICLE_CONFIGURATION_HPP
