# Install script for directory: E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/Program Files (x86)/CyberpunkArchipelagoNative")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/mbedtls" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/aes.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/aria.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/asn1.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/asn1write.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/base64.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/bignum.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/block_cipher.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/build_info.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/camellia.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/ccm.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/chacha20.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/chachapoly.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/check_config.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/cipher.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/cmac.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/compat-2.x.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/config_adjust_legacy_crypto.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/config_adjust_legacy_from_psa.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/config_adjust_psa_from_legacy.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/config_adjust_psa_superset_legacy.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/config_adjust_ssl.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/config_adjust_x509.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/config_psa.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/constant_time.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/ctr_drbg.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/debug.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/des.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/dhm.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/ecdh.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/ecdsa.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/ecjpake.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/ecp.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/entropy.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/error.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/gcm.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/hkdf.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/hmac_drbg.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/lms.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/mbedtls_config.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/md.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/md5.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/memory_buffer_alloc.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/net_sockets.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/nist_kw.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/oid.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/pem.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/pk.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/pkcs12.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/pkcs5.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/pkcs7.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/platform.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/platform_time.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/platform_util.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/poly1305.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/private_access.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/psa_util.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/ripemd160.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/rsa.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/sha1.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/sha256.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/sha3.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/sha512.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/ssl.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/ssl_cache.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/ssl_ciphersuites.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/ssl_cookie.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/ssl_ticket.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/threading.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/timing.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/version.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/x509.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/x509_crl.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/x509_crt.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/mbedtls/x509_csr.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/psa" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/build_info.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_adjust_auto_enabled.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_adjust_config_dependencies.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_adjust_config_key_pair_types.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_adjust_config_synonyms.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_builtin_composites.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_builtin_key_derivation.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_builtin_primitives.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_compat.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_config.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_driver_common.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_driver_contexts_composites.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_driver_contexts_key_derivation.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_driver_contexts_primitives.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_extra.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_legacy.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_platform.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_se_driver.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_sizes.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_struct.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_types.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4/include/psa/crypto_values.h"
    )
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls_bin/include/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
