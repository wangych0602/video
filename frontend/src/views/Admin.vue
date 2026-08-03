<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDevices, registerDevice, startLive, stopLive } from '@/api/devices'
import { createBuilding, createSchool, deleteBuilding, getBuildings, getSchools } from '@/api/schools'
import { createAlbum, deleteAlbum, getAlbums } from '@/api/studio'
import { createUser, getUsers } from '@/api/users'
import { approveVideo, getPendingVideos, getVideos, rejectVideo } from '@/api/videos'
import type { Building, Device, School, UserRecord, Video, VideoAlbum } from '@/api/types'
import { formatDateTime } from '@/utils/format'

const { t } = useI18n()

const activeTab = ref<'pending' | 'albums' | 'devices' | 'users' | 'schools' | 'buildings'>('pending')
const pendingVideos = ref<Video[]>([])
const devices = ref<Device[]>([])
const users = ref<UserRecord[]>([])
const schools = ref<School[]>([])
const buildings = ref<Building[]>([])
const albums = ref<VideoAlbum[]>([])
const loadingPending = ref(false)
const loadingDevices = ref(false)
const loadingUsers = ref(false)
const loadingAlbums = ref(false)
const loadingBuildings = ref(false)
const showRegister = ref(false)
const registering = ref(false)
const registerForm = ref({
  device_name: '',
  device_sn: '',
  device_type: 'recording_host',
  manufacturer: '',
  school: undefined as number | undefined,
})
const showUserDialog = ref(false)
const creatingUser = ref(false)
const userForm = ref({
  username: '',
  email: '',
  password: '',
  role: 'student',
  school: undefined as number | undefined,
})
const showSchoolDialog = ref(false)
const creatingSchool = ref(false)
const schoolForm = ref({
  name: '',
  building: undefined as number | undefined,
})

const showBuildingDialog = ref(false)
const creatingBuilding = ref(false)
const buildingForm = ref({ name: '', description: '' })
const showAlbumDialog = ref(false)
const creatingAlbum = ref(false)
const albumForm = ref({ name: '', description: '' })

const roleLabel = (key: string) => t('role.' + key)

async function loadPending() {
  loadingPending.value = true
  try {
    const data = await getPendingVideos(1)
    pendingVideos.value = data.results
  } finally {
    loadingPending.value = false
  }
}

async function loadDevices() {
  loadingDevices.value = true
  try {
    const data = await getDevices()
    devices.value = data.results
  } finally {
    loadingDevices.value = false
  }
}

async function loadUsers() {
  loadingUsers.value = true
  try {
    const data = await getUsers()
    users.value = data.results
  } finally {
    loadingUsers.value = false
  }
}

async function loadSchoolsList() {
  const data = await getSchools()
  schools.value = data.results
}

async function loadBuildings() {
  loadingBuildings.value = true
  try {
    const data = await getBuildings()
    buildings.value = data.results
  } finally {
    loadingBuildings.value = false
  }
}

async function submitBuilding() {
  if (!buildingForm.value.name.trim()) {
    ElMessage.warning(t('admin.buildingWarn'))
    return
  }
  creatingBuilding.value = true
  try {
    await createBuilding({
      name: buildingForm.value.name.trim(),
      description: buildingForm.value.description.trim(),
    })
    ElMessage.success(t('admin.buildingSuccess'))
    showBuildingDialog.value = false
    buildingForm.value = { name: '', description: '' }
    void loadBuildings()
  } finally {
    creatingBuilding.value = false
  }
}

async function handleDeleteBuilding(building: Building) {
  await ElMessageBox.confirm(t('admin.buildingConfirmDelete', { name: building.name }), t('admin.deleteBuilding'), {
    confirmButtonText: t('common.delete'),
    cancelButtonText: t('common.cancel'),
  })
  await deleteBuilding(building.id)
  ElMessage.success(t('admin.deleted'))
  void loadBuildings()
}

async function openRegister() {
  showRegister.value = true
  if (!schools.value.length) {
    const data = await getSchools()
    schools.value = data.results
  }
}

async function submitRegister() {
  if (!registerForm.value.device_sn.trim() || !registerForm.value.school) {
    ElMessage.warning(t('admin.registerWarn'))
    return
  }
  registering.value = true
  try {
    const result = await registerDevice({
      device_sn: registerForm.value.device_sn.trim(),
      device_name: registerForm.value.device_name.trim(),
      device_type: registerForm.value.device_type,
      manufacturer: registerForm.value.manufacturer.trim(),
      school: registerForm.value.school,
    })
    showRegister.value = false
    await ElMessageBox.alert(
      t('admin.registerDeviceId') + '：' + result.device_id + '\n' + t('admin.registerDeviceToken') + '：' + result.device_token,
      t('admin.registerSuccess'),
      { confirmButtonText: t('common.ok') },
    )
    registerForm.value = {
      device_name: '',
      device_sn: '',
      device_type: 'recording_host',
      manufacturer: '',
      school: undefined,
    }
    void loadDevices()
  } finally {
    registering.value = false
  }
}

async function openUserDialog() {
  showUserDialog.value = true
  if (!schools.value.length) {
    await loadSchoolsList()
  }
}

async function submitUser() {
  if (!userForm.value.username.trim() || !userForm.value.password) {
    ElMessage.warning(t('admin.userWarn'))
    return
  }
  creatingUser.value = true
  try {
    await createUser({
      username: userForm.value.username.trim(),
      email: userForm.value.email.trim(),
      password: userForm.value.password,
      role: userForm.value.role,
      school: userForm.value.school || null,
    })
    ElMessage.success(t('admin.userSuccess'))
    showUserDialog.value = false
    userForm.value = {
      username: '',
      email: '',
      password: '',
      role: 'student',
      school: undefined,
    }
    void loadUsers()
  } finally {
    creatingUser.value = false
  }
}

async function submitSchool() {
  if (!schoolForm.value.name.trim()) {
    ElMessage.warning(t('admin.roomWarn'))
    return
  }
  creatingSchool.value = true
  try {
    await createSchool({
      name: schoolForm.value.name.trim(),
      building: schoolForm.value.building || null,
    })
    ElMessage.success(t('admin.roomSuccess'))
    showSchoolDialog.value = false
    schoolForm.value = {
      name: '',
      building: undefined,
    }
    void loadSchoolsList()
  } finally {
    creatingSchool.value = false
  }
}

async function handleApprove(video: Video) {
  await approveVideo(video.id)
  ElMessage.success(t('admin.approvedMsg', { title: video.title }))
  void loadPending()
}

async function handleReject(video: Video) {
  const result = await ElMessageBox.prompt(t('admin.rejectPrompt'), t('admin.rejectTitle'), {
    confirmButtonText: t('common.confirm'),
    cancelButtonText: t('common.cancel'),
    inputPlaceholder: t('admin.rejectPlaceholder'),
    inputValidator: (value: string) => (value.trim() ? true : t('admin.rejectRequired')),
  })
  await rejectVideo(video.id, result.value.trim())
  ElMessage.success(t('admin.rejectedMsg', { title: video.title }))
  void loadPending()
}

async function handleStartLive(device: Device) {
  const result = await ElMessageBox.prompt(t('admin.livePrompt'), t('admin.liveStart'), {
    confirmButtonText: t('admin.liveStartBtn'),
    cancelButtonText: t('admin.liveCancelBtn'),
    inputValue: device.device_name + ' ' + t('status.live'),
  })
  const live = await startLive(device.id, result.value.trim() || device.device_name + ' ' + t('status.live'))
  await ElMessageBox.alert(
    t('admin.livePushUrl') + '：' + live.stream_url + '\n' + t('admin.liveHlsUrl') + '：' + live.hls_url,
    t('admin.liveCreated'),
    { confirmButtonText: t('common.ok') },
  )
  void loadDevices()
}

async function handleStopLive(device: Device) {
  await stopLive(device.id)
  ElMessage.success(t('admin.liveStopped'))
  void loadDevices()
}

const statusLabel = (key: string) => t('status.' + key)

async function loadAlbums() {
  loadingAlbums.value = true
  try {
    const data = await getAlbums()
    albums.value = data.results
  } finally {
    loadingAlbums.value = false
  }
}

async function submitAlbum() {
  if (!albumForm.value.name.trim()) {
    ElMessage.warning(t('teacher.albumWarnName'))
    return
  }
  creatingAlbum.value = true
  try {
    const data = new FormData()
    data.append('name', albumForm.value.name.trim())
    data.append('description', albumForm.value.description.trim())
    await createAlbum(data)
    ElMessage.success(t('teacher.albumSuccess'))
    showAlbumDialog.value = false
    albumForm.value = { name: '', description: '' }
    void loadAlbums()
  } finally {
    creatingAlbum.value = false
  }
}

async function handleDeleteAlbum(album: VideoAlbum) {
  await ElMessageBox.confirm(t('teacher.albumConfirmDelete', { name: album.name }), t('teacher.albumDeleteTitle'), { confirmButtonText: t('common.delete'), cancelButtonText: t('common.cancel') })
  await deleteAlbum(album.id)
  ElMessage.success(t('teacher.albumDeleted'))
  void loadAlbums()
}

onMounted(() => {
  void loadPending()
  void loadDevices()
  void loadUsers()
  void loadSchoolsList()
  void loadBuildings()
  void loadAlbums()
})
</script>

<template>
  <div class="admin-page">
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="t('admin.tabPending')" name="pending">
        <div class="page-block">
          <el-table v-loading="loadingPending" :data="pendingVideos">
            <el-table-column prop="title" :label="t('admin.colTitle')" min-width="240" />
            <el-table-column :label="t('admin.colTime')" width="170">
              <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column :label="t('admin.colSize')" width="110">
              <template #default="{ row }">
                {{ row.file_size ? `${(row.file_size / 1024 / 1024).toFixed(1)} MB` : '-' }}
              </template>
            </el-table-column>
            <el-table-column :label="t('admin.colAction')" width="180">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="handleApprove(row)">{{ t('admin.approve') }}</el-button>
                <el-button type="danger" size="small" @click="handleReject(row)">{{ t('admin.reject') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loadingPending && pendingVideos.length === 0" :description="t('admin.emptyPending')" />
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('admin.tabDevices')" name="devices">
        <div class="page-block">
          <div class="tab-toolbar">
            <el-button type="primary" @click="openRegister">{{ t('admin.register') }}</el-button>
          </div>
          <el-table v-loading="loadingDevices" :data="devices">
            <el-table-column prop="device_name" :label="t('admin.colDeviceName')" min-width="160" />
            <el-table-column prop="device_sn" :label="t('admin.colSn')" min-width="180" />
            <el-table-column prop="device_type" :label="t('admin.colType')" width="130" />
            <el-table-column :label="t('admin.colRoom')" width="120">
              <template #default="{ row }">{{ row.school_name || '-' }}</template>
            </el-table-column>
            <el-table-column :label="t('admin.colStatus')" width="110">
              <template #default="{ row }">
                <el-tag :type="row.status === 'online' || row.status === 'streaming' ? 'success' : row.status === 'error' ? 'danger' : 'info'">
                  {{ statusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('admin.colLastOnline')" width="170">
              <template #default="{ row }">{{ formatDateTime(row.last_online_time) }}</template>
            </el-table-column>
            <el-table-column :label="t('admin.colAction')" width="160">
              <template #default="{ row }">
                <el-button v-if="row.status === 'online'" type="primary" size="small" @click="handleStartLive(row)">{{ t('common.startLive') }}</el-button>
                <el-button v-if="row.status === 'streaming'" type="danger" size="small" @click="handleStopLive(row)">{{ t('common.stopLive') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loadingDevices && devices.length === 0" :description="t('admin.emptyDevices')" />
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('admin.tabUsers')" name="users">
        <div class="page-block">
          <div class="tab-toolbar">
            <el-button type="primary" @click="openUserDialog">{{ t('admin.createUser') }}</el-button>
          </div>
          <el-table v-loading="loadingUsers" :data="users">
            <el-table-column prop="username" :label="t('admin.colUsername')" min-width="140" />
            <el-table-column prop="email" :label="t('admin.colEmail')" min-width="200" />
            <el-table-column :label="t('admin.colRole')" width="130">
              <template #default="{ row }">{{ roleLabel(row.role) }}</template>
            </el-table-column>
            <el-table-column :label="t('admin.colUserRoom')" width="180">
              <template #default="{ row }">
                {{ schools.find((item) => item.id === row.school)?.name || '-' }}
              </template>
            </el-table-column>
            <el-table-column :label="t('admin.colUserTime')" width="170">
              <template #default="{ row }">{{ formatDateTime(row.date_joined) }}</template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loadingUsers && users.length === 0" :description="t('admin.emptyUsers')" />
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('admin.tabRooms')" name="schools">
        <div class="page-block">
          <div class="tab-toolbar">
            <el-button type="primary" @click="showSchoolDialog = true">{{ t('admin.createRoom') }}</el-button>
          </div>
          <el-table :data="schools">
            <el-table-column prop="name" :label="t('admin.colRoomName')" min-width="220" />
            <el-table-column :label="t('admin.colBuilding')" min-width="160">
              <template #default="{ row }">{{ row.building_name || '-' }}</template>
            </el-table-column>
            <el-table-column :label="t('admin.colRoomTime')" width="170">
              <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
            </el-table-column>
          </el-table>
          <el-empty v-if="schools.length === 0" :description="t('admin.emptyRooms')" />
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('admin.tabBuildings')" name="buildings">
        <div class="page-block">
          <div class="tab-toolbar">
            <el-button type="primary" @click="showBuildingDialog = true">{{ t('admin.createBuilding') }}</el-button>
          </div>
          <el-table v-loading="loadingBuildings" :data="buildings">
            <el-table-column prop="name" :label="t('admin.colBuildingName')" min-width="200" />
            <el-table-column prop="description" :label="t('admin.colBuildingDesc')" min-width="260" show-overflow-tooltip />
            <el-table-column :label="t('admin.colBuildingTime')" width="170">
              <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column :label="t('admin.colAction')" width="100">
              <template #default="{ row }">
                <el-button type="danger" size="small" @click="handleDeleteBuilding(row)">{{ t('common.delete') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loadingBuildings && buildings.length === 0" :description="t('admin.emptyBuildings')" />
        </div>
      </el-tab-pane>
      <el-tab-pane :label="t('admin.tabAlbums')" name="albums">
        <div class="page-block">
          <div class="tab-toolbar">
            <el-button type="primary" @click="showAlbumDialog = true">{{ t('teacher.albumCreate') }}</el-button>
          </div>
          <el-table v-loading="loadingAlbums" :data="albums">
            <el-table-column prop="name" :label="t('teacher.albumName')" min-width="220" />
            <el-table-column prop="description" :label="t('teacher.albumDesc')" min-width="260" show-overflow-tooltip />
            <el-table-column :label="t('teacher.albumCount')" width="90">
              <template #default="{ row }">{{ row.videos?.length || 0 }}</template>
            </el-table-column>
            <el-table-column :label="t('teacher.albumTime')" width="170">
              <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column :label="t('teacher.albumAction')" width="100">
              <template #default="{ row }">
                <el-button type="danger" size="small" @click="handleDeleteAlbum(row)">{{ t('common.delete') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loadingAlbums && albums.length === 0" :description="t('teacher.albumEmpty')" />
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showRegister" :title="t('admin.registerTitle')" width="480px">
      <el-form label-position="top">
        <el-form-item :label="t('admin.registerName')">
          <el-input v-model="registerForm.device_name" :placeholder="t('admin.registerNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.registerSn')">
          <el-input v-model="registerForm.device_sn" :placeholder="t('admin.registerSnPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.registerType')">
          <el-select v-model="registerForm.device_type">
            <el-option :label="t('deviceType.recording_host')" value="recording_host" />
            <el-option :label="t('deviceType.camera')" value="camera" />
            <el-option :label="t('deviceType.microphone')" value="microphone" />
            <el-option :label="t('deviceType.speaker')" value="speaker" />
            <el-option :label="t('deviceType.terminal')" value="terminal" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('admin.registerManufacturer')">
          <el-input v-model="registerForm.manufacturer" :placeholder="t('admin.registerManufacturerPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.registerRoom')">
          <el-select v-model="registerForm.school" :placeholder="t('admin.registerRoomPlaceholder')">
            <el-option v-for="school in schools" :key="school.id" :label="school.name" :value="school.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRegister = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="registering" @click="submitRegister">{{ t('common.register') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showUserDialog" :title="t('admin.userDialogTitle')" width="480px">
      <el-form label-position="top">
        <el-form-item :label="t('admin.userName')">
          <el-input v-model="userForm.username" :placeholder="t('admin.userNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.userEmail')">
          <el-input v-model="userForm.email" :placeholder="t('admin.userEmailPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.userPassword')">
          <el-input v-model="userForm.password" type="password" show-password :placeholder="t('admin.userPasswordPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.userRole')">
          <el-select v-model="userForm.role">
            <el-option :label="t('role.admin')" value="admin" />
            <el-option :label="t('role.school_admin')" value="school_admin" />
            <el-option :label="t('role.teacher')" value="teacher" />
            <el-option :label="t('role.student')" value="student" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('admin.userRoom')">
          <el-select v-model="userForm.school" :placeholder="t('admin.userRoomPlaceholder')" clearable>
            <el-option v-for="school in schools" :key="school.id" :label="school.name" :value="school.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUserDialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="creatingUser" @click="submitUser">{{ t('common.create') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showSchoolDialog" :title="t('admin.roomDialogTitle')" width="480px">
      <el-form label-position="top">
        <el-form-item :label="t('admin.roomName')">
          <el-input v-model="schoolForm.name" :placeholder="t('admin.roomNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.roomBuilding')">
          <el-select v-model="schoolForm.building" :placeholder="t('admin.roomBuildingPlaceholder')" clearable>
            <el-option v-for="item in buildings" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSchoolDialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="creatingSchool" @click="submitSchool">{{ t('common.create') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBuildingDialog" :title="t('admin.buildingDialogTitle')" width="480px">
      <el-form label-position="top">
        <el-form-item :label="t('admin.buildingName')">
          <el-input v-model="buildingForm.name" :placeholder="t('admin.buildingNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.buildingDesc')">
          <el-input v-model="buildingForm.description" type="textarea" :rows="3" :placeholder="t('admin.buildingDescPlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBuildingDialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="creatingBuilding" @click="submitBuilding">{{ t('common.create') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAlbumDialog" :title="t('teacher.albumDialogTitle')" width="480px">
      <el-form label-position="top">
        <el-form-item :label="t('teacher.albumNameLabel')">
          <el-input v-model="albumForm.name" :placeholder="t('teacher.albumName')" />
        </el-form-item>
        <el-form-item :label="t('teacher.albumDescLabel')">
          <el-input v-model="albumForm.description" type="textarea" :rows="3" :placeholder="t('teacher.albumDesc')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAlbumDialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="creatingAlbum" @click="submitAlbum">{{ t('common.create') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.tab-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 14px;
}
</style>
