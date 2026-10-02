// License: LGPL-3.0 License (c) find-sec-bugs
// scaffold: dependencies=com.hazelcast.hazelcast@3.12.12
package crypto

import com.hazelcast.config.Config
import com.hazelcast.config.MapConfig
import com.hazelcast.config.NetworkConfig
import com.hazelcast.config.SymmetricEncryptionConfig
import com.hazelcast.core.Hazelcast
import com.hazelcast.core.IMap

class HazelcastSymmetricEncryption {
    var cacheMap: IMap<String, String>? = null

    fun init() {
        // Specific map time to live

        val myMapConfig: MapConfig = MapConfig()
        myMapConfig.setName("cachetest")
        myMapConfig.setTimeToLiveSeconds(10)

        // Package config
        val myConfig: Config = Config()
        myConfig.addMapConfig(myMapConfig)

        // Symmetric Encryption
        // ruleid: android.gitlab.kotlin_crypto_rule-HazelcastSymmetricEncryption
        val symmetricEncryptionConfig: SymmetricEncryptionConfig = SymmetricEncryptionConfig()
        symmetricEncryptionConfig.setAlgorithm("DESede")
        symmetricEncryptionConfig.setSalt("saltysalt")
        symmetricEncryptionConfig.setPassword("lamepassword")
        symmetricEncryptionConfig.setIterationCount(1337)

        // Weak Network config..
        val networkConfig: NetworkConfig = NetworkConfig()
        networkConfig.setSymmetricEncryptionConfig(symmetricEncryptionConfig)

        myConfig.setNetworkConfig(networkConfig)

        Hazelcast.newHazelcastInstance(myConfig)

        cacheMap = Hazelcast.getOrCreateHazelcastInstance().getMap("cachetest")
    }

    fun put(key: String?, value: String?) {
        cacheMap?.put(key, value)
    }

    fun get(key: String?): String? {
        return cacheMap?.get(key)
    }
}