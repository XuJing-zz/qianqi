# 前端函数调用关系表

> 由 `tools/function-map.mjs` 自动生成。
> 「定义位置」是原函数真正写在哪里；「调用位置」是其他文件 import/使用它的地方。

## 速查：被页面调用最多的函数

| 函数 | 原函数定义 | 调用页面数 | 导入次数 |
|---|---|---|---|
| `authState` | `store/index.js:374` | 29 | 30 |
| `default` | `views/user/common/nav.vue:40` | 19 | 19 |
| `addLog` | `store/heritageSystem.js:137` | 17 | 17 |
| `heritageProducts` | `store/heritageProducts.js:8` | 15 | 16 |
| `default` | `views/admin/AdminLayout.vue:1` | 14 | 14 |
| `loadProducts` | `store/heritageProducts.js:40` | 14 | 14 |
| `usePagedList` | `composables/usePagedList.js:7` | 11 | 11 |
| `heritageSkills` | `store/heritageSkills.js:8` | 11 | 11 |
| `mapKeys` | `api/utils.js:21` | 10 | 22 |
| `loadSkills` | `store/heritageSkills.js:45` | 10 | 10 |
| `heritageCourses` | `store/heritageCourses.js:8` | 10 | 10 |
| `courses` | `store/courses.js:7` | 9 | 9 |
| `ensureCourses` | `store/courses.js:71` | 9 | 9 |
| `default` | `views/console/ConsoleLayout.vue:1` | 9 | 9 |
| `loadInheritors` | `store/heritageInheritors.js:42` | 8 | 9 |
| `inheritors` | `store/heritageInheritors.js:13` | 8 | 8 |
| `checkUploadFile` | `store/heritageSystem.js:63` | 8 | 8 |
| `loadHeritageCourses` | `store/heritageCourses.js:63` | 8 | 8 |
| `isLoggedIn` | `store/index.js:412` | 7 | 10 |
| `brandLogo` | `store/heritageSystem.js:20` | 5 | 5 |
| `brandGlyph` | `store/heritageSystem.js:21` | 5 | 5 |
| `brandShort` | `store/heritageSystem.js:22` | 5 | 5 |
| `productStatusMap` | `store/heritageProducts.js:11` | 5 | 5 |
| `uploadLimitMb` | `store/heritageSystem.js:32` | 5 | 5 |
| `default` | `views/user/profile/ProfileAside.vue:1` | 5 | 5 |
| `listStudents` | `api/students.js:7` | 4 | 6 |
| `loadConfig` | `store/heritageSystem.js:173` | 4 | 5 |
| `heritageStudents` | `store/heritageStudents.js:8` | 4 | 5 |
| `homeConfig` | `store/heritageSystem.js:102` | 4 | 4 |
| `logout` | `store/index.js:402` | 4 | 4 |

## API 层（api/）

### `createAccount`

- 原函数定义：`api/accounts.js:13`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageAccounts.js:4`

### `deleteAccount`

- 原函数定义：`api/accounts.js:43`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageAccounts.js:4`（本地名 `apiDeleteAccount`）

### `issueInheritor`

- 原函数定义：`api/accounts.js:25`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageAccounts.js:4`

### `listAccounts`

- 原函数定义：`api/accounts.js:7`
- 被 1 个页面文件调用，共 2 处导入：
  - 模块 `store/heritageAccounts.js:4`
  - 页面 `views/admin/AdminAccounts.vue:144`

### `resetAccountPassword`

- 原函数定义：`api/accounts.js:37`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageAccounts.js:4`

### `toggleAccountStatus`

- 原函数定义：`api/accounts.js:31`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageAccounts.js:4`（本地名 `apiToggleStatus`）

### `updateAccount`

- 原函数定义：`api/accounts.js:19`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageAccounts.js:4`（本地名 `apiUpdateAccount`）

### `createAddress`

- 原函数定义：`api/addresses.js:10`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/userAddresses.js:3`

### `deleteAddress`

- 原函数定义：`api/addresses.js:18`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/userAddresses.js:3`

### `listAddresses`

- 原函数定义：`api/addresses.js:6`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/userAddresses.js:3`

### `updateAddress`

- 原函数定义：`api/addresses.js:14`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/userAddresses.js:3`

### `apiLogin`

- 原函数定义：`api/auth.js:7`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/index.js:358`

### `apiLogout`

- 原函数定义：`api/auth.js:15`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/index.js:358`

### `apiMe`

- 原函数定义：`api/auth.js:26`
- 被 3 个页面文件调用，共 4 处导入：
  - 模块 `store/heritageProfile.js:3`
  - 页面 `views/user/common/nav.vue:37`
  - 页面 `views/user/profile/Profile.vue:149`
  - 页面 `views/user/profile/ProfileAside.vue:57`

### `apiRegister`

- 原函数定义：`api/auth.js:38`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/auth/Register.vue:144`

### `apiUpdateProfile`

- 原函数定义：`api/auth.js:32`
- 被 1 个页面文件调用，共 2 处导入：
  - 模块 `store/heritageProfile.js:3`
  - 页面 `views/user/profile/Profile.vue:149`

### `api`

- 原函数定义：`api/client.js:139`
- 被 0 个页面文件调用，共 12 处导入：
  - 模块 `api/accounts.js:2`
  - 模块 `api/addresses.js:2`
  - 模块 `api/auth.js:2`
  - 模块 `api/contact.js:2`
  - 模块 `api/courses.js:2`
  - 模块 `api/heritage.js:2`
  - 模块 `api/inventory.js:2`
  - 模块 `api/orders.js:2`
  - 模块 `api/products.js:2`
  - 模块 `api/skills.js:2`
  - 模块 `api/students.js:2`
  - 模块 `api/system.js:2`

### `clearTokens`

- 原函数定义：`api/client.js:24`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `api/auth.js:2`

### `setTokens`

- 原函数定义：`api/client.js:19`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `api/auth.js:2`

### `handleContactMessage`

- 原函数定义：`api/contact.js:19`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/contactMessages.js:3`

### `listContactMessages`

- 原函数定义：`api/contact.js:13`
- 被 1 个页面文件调用，共 2 处导入：
  - 模块 `store/contactMessages.js:3`
  - 页面 `views/admin/AdminMessages.vue:102`

### `removeContactMessage`

- 原函数定义：`api/contact.js:25`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/contactMessages.js:3`

### `submitContactMessage`

- 原函数定义：`api/contact.js:7`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/about/Contact.vue:88`

### `createCourse`

- 原函数定义：`api/courses.js:12`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageCourses.js:3`

### `getCourse`

- 原函数定义：`api/courses.js:22`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/courses.js:3`

### `listCourses`

- 原函数定义：`api/courses.js:7`
- 被 1 个页面文件调用，共 3 处导入：
  - 模块 `store/courses.js:3`
  - 模块 `store/heritageCourses.js:3`
  - 页面 `views/admin/AdminCourses.vue:222`

### `listVideoReviews`

- 原函数定义：`api/courses.js:42`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminVideos.vue:166`

### `offlineCourse`

- 原函数定义：`api/courses.js:37`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageCourses.js:3`

### `reviewCourse`

- 原函数定义：`api/courses.js:27`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageCourses.js:3`

### `reviewVideo`

- 原函数定义：`api/courses.js:47`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageCourses.js:3`

### `submitCourse`

- 原函数定义：`api/courses.js:32`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageCourses.js:3`

### `updateCourse`

- 原函数定义：`api/courses.js:17`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageCourses.js:3`

### `uploadCourseCover`

- 原函数定义：`api/courses.js:63`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleCourseEdit.vue:268`

### `uploadCourseVideo`

- 原函数定义：`api/courses.js:56`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleCourseEdit.vue:268`

### `apiCreateInheritor`

- 原函数定义：`api/heritage.js:13`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageInheritors.js:3`

### `apiDeleteInheritor`

- 原函数定义：`api/heritage.js:25`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageInheritors.js:3`

### `apiListInheritors`

- 原函数定义：`api/heritage.js:7`
- 被 1 个页面文件调用，共 2 处导入：
  - 模块 `store/heritageInheritors.js:3`
  - 页面 `views/admin/AdminInheritors.vue:164`

### `apiMyInheritor`

- 原函数定义：`api/heritage.js:37`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageProfile.js:4`

### `apiToggleInheritorStatus`

- 原函数定义：`api/heritage.js:31`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageInheritors.js:3`

### `apiUpdateInheritor`

- 原函数定义：`api/heritage.js:19`
- 被 1 个页面文件调用，共 3 处导入：
  - 模块 `store/heritageInheritors.js:3`
  - 模块 `store/heritageProfile.js:4`
  - 页面 `views/console/ConsoleProfile.vue:151`

### `apiUploadCert`

- 原函数定义：`api/heritage.js:43`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminInheritors.vue:164`
  - 页面 `views/console/ConsoleProfile.vue:151`

### `createMaterial`

- 原函数定义：`api/inventory.js:12`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageInventory.js:4`

### `createShipment`

- 原函数定义：`api/inventory.js:44`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageInventory.js:4`

### `deleteMaterial`

- 原函数定义：`api/inventory.js:22`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageInventory.js:4`

### `listMaterials`

- 原函数定义：`api/inventory.js:7`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageInventory.js:4`

### `listShipments`

- 原函数定义：`api/inventory.js:39`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageInventory.js:4`

### `listStockRecords`

- 原函数定义：`api/inventory.js:33`
- 被 1 个页面文件调用，共 2 处导入：
  - 模块 `store/heritageInventory.js:4`
  - 页面 `views/admin/AdminProducts.vue:396`（本地名 `listMaterialStockRecords`）

### `shipShipment`

- 原函数定义：`api/inventory.js:49`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageInventory.js:4`

### `signShipment`

- 原函数定义：`api/inventory.js:54`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageInventory.js:4`

### `stockInOut`

- 原函数定义：`api/inventory.js:27`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageInventory.js:4`

### `updateMaterial`

- 原函数定义：`api/inventory.js:17`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageInventory.js:4`

### `auditOrder`

- 原函数定义：`api/orders.js:28`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:355`

### `buyProductOrder`

- 原函数定义：`api/orders.js:13`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/index.js:11`

### `cancelOrder`

- 原函数定义：`api/orders.js:25`
- 被 0 个页面文件调用，共 2 处导入：
  - 模块 `store/heritageOrders.js:3`
  - 模块 `store/index.js:11`

### `completeOrder`

- 原函数定义：`api/orders.js:22`
- 被 0 个页面文件调用，共 2 处导入：
  - 模块 `store/heritageOrders.js:3`
  - 模块 `store/index.js:11`

### `createOrder`

- 原函数定义：`api/orders.js:10`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/index.js:11`

### `listOrders`

- 原函数定义：`api/orders.js:7`
- 被 1 个页面文件调用，共 3 处导入：
  - 模块 `store/heritageOrders.js:3`
  - 模块 `store/index.js:11`
  - 页面 `views/admin/AdminOrders.vue:355`

### `manualCreateOrder`

- 原函数定义：`api/orders.js:31`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:355`

### `payOrder`

- 原函数定义：`api/orders.js:16`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/index.js:11`

### `setOrderStatus`

- 原函数定义：`api/orders.js:34`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:355`

### `shipOrder`

- 原函数定义：`api/orders.js:19`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageOrders.js:3`

### `addFavorite`

- 原函数定义：`api/products.js:59`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/index.js:7`

### `createProduct`

- 原函数定义：`api/products.js:12`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageProducts.js:3`

### `deleteProduct`

- 原函数定义：`api/products.js:22`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageProducts.js:3`

### `fetchProductFilters`

- 原函数定义：`api/products.js:37`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminProducts.vue:394`

### `listFavorites`

- 原函数定义：`api/products.js:54`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/index.js:7`

### `listProducts`

- 原函数定义：`api/products.js:7`
- 被 3 个页面文件调用，共 4 处导入：
  - 模块 `store/heritageProducts.js:3`
  - 页面 `views/admin/AdminOrders.vue:356`
  - 页面 `views/admin/AdminProductReview.vue:212`
  - 页面 `views/admin/AdminProducts.vue:394`

### `listStockRecords`

- 原函数定义：`api/products.js:48`
- 被 2 个页面文件调用，共 3 处导入：
  - 模块 `store/heritageProductInventory.js:4`
  - 页面 `views/admin/AdminProducts.vue:395`（本地名 `listProductStockRecords`）
  - 页面 `views/console/ConsoleInventory.vue:178`

### `removeFavorite`

- 原函数定义：`api/products.js:64`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/index.js:7`

### `reviewProduct`

- 原函数定义：`api/products.js:27`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageProducts.js:3`

### `stockInOut`

- 原函数定义：`api/products.js:43`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageProductInventory.js:4`（本地名 `apiStockInOut`）

### `submitProduct`

- 原函数定义：`api/products.js:32`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageProducts.js:3`

### `updateProduct`

- 原函数定义：`api/products.js:17`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageProducts.js:3`

### `createSkill`

- 原函数定义：`api/skills.js:12`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageSkills.js:3`

### `deleteSkill`

- 原函数定义：`api/skills.js:18`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageSkills.js:3`

### `listSkillCategories`

- 原函数定义：`api/skills.js:9`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleCourseEdit.vue:269`

### `listSkills`

- 原函数定义：`api/skills.js:6`
- 被 1 个页面文件调用，共 2 处导入：
  - 模块 `store/heritageSkills.js:3`
  - 页面 `views/admin/AdminSkills.vue:308`

### `reviewSkill`

- 原函数定义：`api/skills.js:21`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageSkills.js:3`

### `submitSkill`

- 原函数定义：`api/skills.js:24`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageSkills.js:3`

### `toggleSkillOffline`

- 原函数定义：`api/skills.js:27`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageSkills.js:3`

### `updateSkill`

- 原函数定义：`api/skills.js:15`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageSkills.js:3`

### `uploadSkillDoc`

- 原函数定义：`api/skills.js:37`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleSkills.vue:384`

### `uploadSkillImage`

- 原函数定义：`api/skills.js:30`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleSkills.vue:384`

### `approveStudent`

- 原函数定义：`api/students.js:22`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminStudents.vue:101`

### `createStudent`

- 原函数定义：`api/students.js:10`
- 被 0 个页面文件调用，共 2 处导入：
  - 模块 `store/heritageStudents.js:3`
  - 模块 `store/index.js:10`

### `createTrainingRecord`

- 原函数定义：`api/students.js:33`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageTrainingRecords.js:3`

### `deleteStudent`

- 原函数定义：`api/students.js:16`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageStudents.js:3`

### `deleteTrainingRecord`

- 原函数定义：`api/students.js:39`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageTrainingRecords.js:3`

### `exportTrainingRecords`

- 原函数定义：`api/students.js:44`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminTraining.vue:149`
  - 页面 `views/console/ConsoleTraining.vue:183`

### `listStudents`

- 原函数定义：`api/students.js:7`
- 被 4 个页面文件调用，共 6 处导入：
  - 模块 `store/heritageStudents.js:3`
  - 模块 `store/index.js:10`
  - 页面 `views/admin/AdminStudents.vue:101`
  - 页面 `views/admin/AdminTraining.vue:149`
  - 页面 `views/console/ConsoleStudents.vue:250`
  - 页面 `views/console/ConsoleTraining.vue:183`

### `listTrainingRecords`

- 原函数定义：`api/students.js:30`
- 被 1 个页面文件调用，共 2 处导入：
  - 模块 `store/heritageTrainingRecords.js:3`
  - 页面 `views/admin/AdminTraining.vue:149`

### `markStudentDone`

- 原函数定义：`api/students.js:19`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageStudents.js:3`

### `rejectStudent`

- 原函数定义：`api/students.js:25`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminStudents.vue:101`

### `updateStudent`

- 原函数定义：`api/students.js:13`
- 被 0 个页面文件调用，共 2 处导入：
  - 模块 `store/heritageStudents.js:3`
  - 模块 `store/index.js:10`

### `updateTrainingRecord`

- 原函数定义：`api/students.js:36`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageTrainingRecords.js:3`

### `createLog`

- 原函数定义：`api/system.js:12`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageSystem.js:3`

### `exportLogs`

- 原函数定义：`api/system.js:19`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminLogs.vue:59`

### `getConfig`

- 原函数定义：`api/system.js:42`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageSystem.js:3`

### `initData`

- 原函数定义：`api/system.js:57`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminConfig.vue:181`

### `listLogs`

- 原函数定义：`api/system.js:7`
- 被 1 个页面文件调用，共 2 处导入：
  - 模块 `store/heritageSystem.js:3`
  - 页面 `views/admin/AdminLogs.vue:59`

### `saveConfig`

- 原函数定义：`api/system.js:47`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageSystem.js:3`

### `uploadLogo`

- 原函数定义：`api/system.js:52`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `store/heritageSystem.js:3`

### `mapKeys`

- 原函数定义：`api/utils.js:21`
- 被 10 个页面文件调用，共 22 处导入：
  - 模块 `store/courses.js:4`
  - 模块 `store/heritageAccounts.js:5`
  - 模块 `store/heritageCourses.js:4`
  - 模块 `store/heritageInventory.js:9`
  - 模块 `store/heritageOrders.js:4`
  - 模块 `store/heritageProductInventory.js:5`
  - 模块 `store/heritageProducts.js:4`
  - 模块 `store/heritageSkills.js:4`
  - 模块 `store/heritageStudents.js:4`
  - 模块 `store/heritageTrainingRecords.js:9`
  - 模块 `store/index.js:12`
  - 模块 `store/userAddresses.js:4`
  - 页面 `views/admin/AdminAccounts.vue:145`
  - 页面 `views/admin/AdminCourses.vue:223`
  - 页面 `views/admin/AdminOrders.vue:357`
  - 页面 `views/admin/AdminProductReview.vue:213`
  - 页面 `views/admin/AdminProducts.vue:397`
  - 页面 `views/admin/AdminSkills.vue:309`
  - 页面 `views/admin/AdminStudents.vue:102`
  - 页面 `views/admin/AdminTraining.vue:150`
  - 页面 `views/admin/AdminVideos.vue:167`
  - 页面 `views/console/ConsoleInventory.vue:179`

### `mapToSnake`

- 原函数定义：`api/utils.js:42`
- 被 0 个页面文件调用，共 8 处导入：
  - 模块 `store/heritageCourses.js:4`
  - 模块 `store/heritageInventory.js:9`
  - 模块 `store/heritageProducts.js:4`
  - 模块 `store/heritageSkills.js:4`
  - 模块 `store/heritageStudents.js:4`
  - 模块 `store/heritageTrainingRecords.js:9`
  - 模块 `store/index.js:12`
  - 模块 `store/userAddresses.js:4`

### `qs`

- 原函数定义：`api/utils.js:57`
- 被 0 个页面文件调用，共 9 处导入：
  - 模块 `api/accounts.js:3`
  - 模块 `api/contact.js:3`
  - 模块 `api/courses.js:3`
  - 模块 `api/heritage.js:3`
  - 模块 `api/inventory.js:3`
  - 模块 `api/orders.js:3`
  - 模块 `api/products.js:3`
  - 模块 `api/students.js:3`
  - 模块 `api/system.js:3`

## 状态层（store/）

### `contactMessages`

- 原函数定义：`store/contactMessages.js:7`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminLayout.vue:77`

### `handleMessageAction`

- 原函数定义：`store/contactMessages.js:47`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminMessages.vue:94`

### `loadContactMessages`

- 原函数定义：`store/contactMessages.js:37`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminLayout.vue:77`

### `messageStatusMap`

- 原函数定义：`store/contactMessages.js:10`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminMessages.vue:94`

### `removeMessageAction`

- 原函数定义：`store/contactMessages.js:62`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminMessages.vue:94`

### `courses`

- 原函数定义：`store/courses.js:7`
- 被 9 个页面文件调用，共 9 处导入：
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/user/archive/SkillDetailPage.vue:285`
  - 页面 `views/user/course/CourseDetail.vue:139`
  - 页面 `views/user/course/CourseList.vue:168`
  - 页面 `views/user/home/Home.vue:111`
  - 页面 `views/user/inheritor/InheritorDetail.vue:146`
  - 页面 `views/user/profile/MyEnroll.vue:97`
  - 页面 `views/user/profile/MyOrder.vue:128`
  - 页面 `views/user/profile/Pay.vue:77`

### `ensureCourses`

- 原函数定义：`store/courses.js:71`
- 被 9 个页面文件调用，共 9 处导入：
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/user/archive/SkillDetailPage.vue:285`
  - 页面 `views/user/course/CourseDetail.vue:139`
  - 页面 `views/user/course/CourseList.vue:168`
  - 页面 `views/user/home/Home.vue:111`
  - 页面 `views/user/inheritor/InheritorDetail.vue:146`
  - 页面 `views/user/profile/MyEnroll.vue:97`
  - 页面 `views/user/profile/MyOrder.vue:128`
  - 页面 `views/user/profile/Pay.vue:77`

### `fetchCourseDetail`

- 原函数定义：`store/courses.js:60`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/MyLearn.vue:119`

### `loadCourses`

- 原函数定义：`store/courses.js:49`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `main.js:9`

### `accountRoleMap`

- 原函数定义：`store/heritageAccounts.js:12`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminAccounts.vue:146`

### `addAccount`

- 原函数定义：`store/heritageAccounts.js:64`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminAccounts.vue:146`

### `issueHeritageAccount`

- 原函数定义：`store/heritageAccounts.js:196`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminAccounts.vue:146`

### `removeAccount`

- 原函数定义：`store/heritageAccounts.js:168`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminAccounts.vue:146`

### `resetPassword`

- 原函数定义：`store/heritageAccounts.js:152`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminAccounts.vue:146`

### `toggleAccountStatus`

- 原函数定义：`store/heritageAccounts.js:118`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminAccounts.vue:146`

### `updateAccountAction`

- 原函数定义：`store/heritageAccounts.js:95`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminAccounts.vue:146`

### `addCourse`

- 原函数定义：`store/heritageCourses.js:73`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleCourseEdit.vue:270`

### `courseStatusMap`

- 原函数定义：`store/heritageCourses.js:19`
- 被 3 个页面文件调用，共 3 处导入：
  - 页面 `views/admin/AdminCourses.vue:224`
  - 页面 `views/console/ConsoleCourseEdit.vue:270`
  - 页面 `views/console/ConsoleCourses.vue:84`

### `durationToLessonCount`

- 原函数定义：`store/heritageCourses.js:146`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleCourseEdit.vue:270`

### `heritageCourses`

- 原函数定义：`store/heritageCourses.js:8`
- 被 10 个页面文件调用，共 10 处导入：
  - 页面 `views/admin/AdminCourses.vue:224`
  - 页面 `views/admin/AdminLayout.vue:77`
  - 页面 `views/admin/AdminOverview.vue:54`
  - 页面 `views/admin/AdminTraining.vue:139`
  - 页面 `views/admin/AdminVideos.vue:168`
  - 页面 `views/console/ConsoleCourseEdit.vue:270`
  - 页面 `views/console/ConsoleCourses.vue:84`
  - 页面 `views/console/ConsoleOverview.vue:147`
  - 页面 `views/console/ConsoleStudents.vue:231`
  - 页面 `views/console/ConsoleTraining.vue:172`

### `loadHeritageCourses`

- 原函数定义：`store/heritageCourses.js:63`
- 被 8 个页面文件调用，共 8 处导入：
  - 页面 `views/admin/AdminLayout.vue:77`
  - 页面 `views/admin/AdminOverview.vue:54`
  - 页面 `views/admin/AdminTraining.vue:139`
  - 页面 `views/console/ConsoleCourseEdit.vue:270`
  - 页面 `views/console/ConsoleCourses.vue:84`
  - 页面 `views/console/ConsoleOverview.vue:147`
  - 页面 `views/console/ConsoleStudents.vue:231`
  - 页面 `views/console/ConsoleTraining.vue:172`

### `offlineCourseAction`

- 原函数定义：`store/heritageCourses.js:108`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminCourses.vue:224`
  - 页面 `views/console/ConsoleCourses.vue:84`

### `reviewCourseAction`

- 原函数定义：`store/heritageCourses.js:120`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminCourses.vue:224`

### `reviewVideoAction`

- 原函数定义：`store/heritageCourses.js:132`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminVideos.vue:168`

### `submitCourseAction`

- 原函数定义：`store/heritageCourses.js:97`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/console/ConsoleCourseEdit.vue:270`
  - 页面 `views/console/ConsoleCourses.vue:84`

### `updateCourseAction`

- 原函数定义：`store/heritageCourses.js:85`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleCourseEdit.vue:270`

### `videoStatusMap`

- 原函数定义：`store/heritageCourses.js:11`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminVideos.vue:168`

### `addInheritor`

- 原函数定义：`store/heritageInheritors.js:53`
- 被 1 个页面文件调用，共 2 处导入：
  - 模块 `store/heritageAccounts.js:3`
  - 页面 `views/admin/AdminInheritors.vue:165`

### `inheritorCrafts`

- 原函数定义：`store/heritageInheritors.js:18`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminInheritors.vue:165`

### `inheritorLevels`

- 原函数定义：`store/heritageInheritors.js:16`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminInheritors.vue:165`

### `inheritors`

- 原函数定义：`store/heritageInheritors.js:13`
- 被 8 个页面文件调用，共 8 处导入：
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/console/ConsoleWorks.vue:192`
  - 页面 `views/user/archive/SkillDetailPage.vue:285`
  - 页面 `views/user/course/CourseDetail.vue:139`
  - 页面 `views/user/home/Home.vue:111`
  - 页面 `views/user/inheritor/InheritorDetail.vue:146`
  - 页面 `views/user/inheritor/InheritorShow.vue:87`
  - 页面 `views/user/product/ProductDetail.vue:201`

### `inheritorStatusMap`

- 原函数定义：`store/heritageInheritors.js:21`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminInheritors.vue:165`

### `loadInheritors`

- 原函数定义：`store/heritageInheritors.js:42`
- 被 8 个页面文件调用，共 9 处导入：
  - 模块 `main.js:9`
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/console/ConsoleWorks.vue:192`
  - 页面 `views/user/archive/SkillDetailPage.vue:285`
  - 页面 `views/user/course/CourseDetail.vue:139`
  - 页面 `views/user/home/Home.vue:111`
  - 页面 `views/user/inheritor/InheritorDetail.vue:146`
  - 页面 `views/user/inheritor/InheritorShow.vue:87`
  - 页面 `views/user/product/ProductDetail.vue:201`

### `removeInheritor`

- 原函数定义：`store/heritageInheritors.js:105`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminInheritors.vue:165`

### `toggleInheritorStatus`

- 原函数定义：`store/heritageInheritors.js:115`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminInheritors.vue:165`

### `updateInheritor`

- 原函数定义：`store/heritageInheritors.js:80`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminInheritors.vue:165`

### `checkStock`

- 原函数定义：`store/heritageInventory.js:227`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`

### `createShipmentAction`

- 原函数定义：`store/heritageInventory.js:242`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`

### `derivedShipments`

- 原函数定义：`store/heritageInventory.js:195`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`

### `getStudentMaterialPlan`

- 原函数定义：`store/heritageInventory.js:161`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleStudents.vue:231`

### `inventoryMaterials`

- 原函数定义：`store/heritageInventory.js:13`
- 被 3 个页面文件调用，共 3 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/console/ConsoleStudents.vue:231`

### `loadMaterials`

- 原函数定义：`store/heritageInventory.js:81`
- 被 3 个页面文件调用，共 3 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/console/ConsoleStudents.vue:231`

### `loadShipments`

- 原函数定义：`store/heritageInventory.js:91`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`

### `materialRecordTypeMap`

- 原函数定义：`store/heritageInventory.js:30`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminProducts.vue:399`

### `materialState`

- 原函数定义：`store/heritageInventory.js:23`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminProducts.vue:399`

### `materialStockInOut`

- 原函数定义：`store/heritageInventory.js:144`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminProducts.vue:399`

### `materialTypeMap`

- 原函数定义：`store/heritageInventory.js:37`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/console/ConsoleStudents.vue:231`

### `setStudentMaterialPlan`

- 原函数定义：`store/heritageInventory.js:170`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleStudents.vue:231`

### `shipments`

- 原函数定义：`store/heritageInventory.js:17`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`

### `shipmentStatusMap`

- 原函数定义：`store/heritageInventory.js:43`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`

### `shipOut`

- 原函数定义：`store/heritageInventory.js:260`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`（本地名 `doShipOut`）

### `signShipmentAction`

- 原函数定义：`store/heritageInventory.js:277`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`

### `cancelOrderAction`

- 原函数定义：`store/heritageOrders.js:71`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`

### `completeOrderAction`

- 原函数定义：`store/heritageOrders.js:82`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`

### `heritageOrders`

- 原函数定义：`store/heritageOrders.js:8`
- 被 3 个页面文件调用，共 3 处导入：
  - 页面 `views/admin/AdminLayout.vue:77`
  - 页面 `views/admin/AdminOrders.vue:358`
  - 页面 `views/admin/AdminOverview.vue:54`

### `loadHeritageOrders`

- 原函数定义：`store/heritageOrders.js:50`
- 被 3 个页面文件调用，共 3 处导入：
  - 页面 `views/admin/AdminLayout.vue:77`
  - 页面 `views/admin/AdminOrders.vue:358`
  - 页面 `views/admin/AdminOverview.vue:54`

### `orderStatusMap`

- 原函数定义：`store/heritageOrders.js:11`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`

### `shipOrderAction`

- 原函数定义：`store/heritageOrders.js:60`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`

### `productStockState`

- 原函数定义：`store/heritageProductInventory.js:60`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/console/ConsoleInventory.vue:177`

### `stockInOut`

- 原函数定义：`store/heritageProductInventory.js:75`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/console/ConsoleInventory.vue:177`

### `stockRecordTypeMap`

- 原函数定义：`store/heritageProductInventory.js:9`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/console/ConsoleInventory.vue:177`

### `addProduct`

- 原函数定义：`store/heritageProducts.js:50`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/console/ConsoleWorks.vue:192`

### `heritageProducts`

- 原函数定义：`store/heritageProducts.js:8`
- 被 15 个页面文件调用，共 16 处导入：
  - 模块 `store/heritageProductInventory.js:3`
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/admin/AdminLayout.vue:77`
  - 页面 `views/admin/AdminOverview.vue:54`
  - 页面 `views/admin/AdminProductReview.vue:214`
  - 页面 `views/admin/AdminSkills.vue:310`
  - 页面 `views/console/ConsoleInventory.vue:177`
  - 页面 `views/console/ConsoleOverview.vue:147`
  - 页面 `views/console/ConsoleSkills.vue:385`
  - 页面 `views/console/ConsoleWorks.vue:192`
  - 页面 `views/user/archive/SkillDetailPage.vue:285`
  - 页面 `views/user/home/Home.vue:111`
  - 页面 `views/user/inheritor/InheritorDetail.vue:146`
  - 页面 `views/user/product/ProductDetail.vue:201`
  - 页面 `views/user/product/ProductList.vue:188`
  - 页面 `views/user/profile/MyOrder.vue:128`

### `loadProducts`

- 原函数定义：`store/heritageProducts.js:40`
- 被 14 个页面文件调用，共 14 处导入：
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/admin/AdminLayout.vue:77`
  - 页面 `views/admin/AdminOverview.vue:54`
  - 页面 `views/admin/AdminSkills.vue:310`
  - 页面 `views/console/ConsoleInventory.vue:177`
  - 页面 `views/console/ConsoleOverview.vue:147`
  - 页面 `views/console/ConsoleSkills.vue:385`
  - 页面 `views/console/ConsoleWorks.vue:192`
  - 页面 `views/user/archive/SkillDetailPage.vue:285`
  - 页面 `views/user/home/Home.vue:111`
  - 页面 `views/user/inheritor/InheritorDetail.vue:146`
  - 页面 `views/user/product/ProductDetail.vue:201`
  - 页面 `views/user/product/ProductList.vue:188`
  - 页面 `views/user/profile/MyOrder.vue:128`

### `productStatusMap`

- 原函数定义：`store/heritageProducts.js:11`
- 被 5 个页面文件调用，共 5 处导入：
  - 页面 `views/admin/AdminProductReview.vue:214`
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/admin/AdminSkills.vue:310`
  - 页面 `views/console/ConsoleInventory.vue:177`
  - 页面 `views/console/ConsoleWorks.vue:192`

### `removeProduct`

- 原函数定义：`store/heritageProducts.js:72`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleWorks.vue:192`

### `reviewProductAction`

- 原函数定义：`store/heritageProducts.js:93`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminProductReview.vue:214`

### `submitProductAction`

- 原函数定义：`store/heritageProducts.js:82`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleWorks.vue:192`

### `updateProductAction`

- 原函数定义：`store/heritageProducts.js:61`
- 被 4 个页面文件调用，共 4 处导入：
  - 页面 `views/admin/AdminProductReview.vue:214`
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/console/ConsoleInventory.vue:177`
  - 页面 `views/console/ConsoleWorks.vue:192`

### `craftOptions`

- 原函数定义：`store/heritageProfile.js:29`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleProfile.vue:152`

### `heritageProfile`

- 原函数定义：`store/heritageProfile.js:9`
- 被 4 个页面文件调用，共 4 处导入：
  - 页面 `views/console/ConsoleOverview.vue:147`
  - 页面 `views/console/ConsoleProfile.vue:152`
  - 页面 `views/console/ConsoleSkills.vue:385`
  - 页面 `views/console/ConsoleWorks.vue:192`

### `levelOptions`

- 原函数定义：`store/heritageProfile.js:26`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleProfile.vue:152`

### `loadHeritageProfile`

- 原函数定义：`store/heritageProfile.js:37`
- 被 4 个页面文件调用，共 4 处导入：
  - 页面 `views/console/ConsoleOverview.vue:147`
  - 页面 `views/console/ConsoleProfile.vue:152`
  - 页面 `views/console/ConsoleSkills.vue:385`
  - 页面 `views/console/ConsoleWorks.vue:192`

### `saveHeritageProfile`

- 原函数定义：`store/heritageProfile.js:81`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleProfile.vue:152`

### `addSkill`

- 原函数定义：`store/heritageSkills.js:55`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleSkills.vue:385`

### `heritageSkills`

- 原函数定义：`store/heritageSkills.js:8`
- 被 11 个页面文件调用，共 11 处导入：
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/admin/AdminLayout.vue:77`
  - 页面 `views/admin/AdminOverview.vue:54`
  - 页面 `views/admin/AdminSkills.vue:310`
  - 页面 `views/console/ConsoleOverview.vue:147`
  - 页面 `views/console/ConsoleSkills.vue:385`
  - 页面 `views/user/archive/ArchiveDetail.vue:18`
  - 页面 `views/user/archive/ArchiveList.vue:102`
  - 页面 `views/user/archive/SkillDetailPage.vue:285`
  - 页面 `views/user/home/Home.vue:111`
  - 页面 `views/user/inheritor/InheritorDetail.vue:146`

### `loadSkills`

- 原函数定义：`store/heritageSkills.js:45`
- 被 10 个页面文件调用，共 10 处导入：
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/admin/AdminLayout.vue:77`
  - 页面 `views/admin/AdminOverview.vue:54`
  - 页面 `views/console/ConsoleOverview.vue:147`
  - 页面 `views/console/ConsoleSkills.vue:385`
  - 页面 `views/user/archive/ArchiveDetail.vue:18`
  - 页面 `views/user/archive/ArchiveList.vue:102`
  - 页面 `views/user/archive/SkillDetailPage.vue:285`
  - 页面 `views/user/home/Home.vue:111`
  - 页面 `views/user/inheritor/InheritorDetail.vue:146`

### `removeSkill`

- 原函数定义：`store/heritageSkills.js:77`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleSkills.vue:385`（本地名 `removeSkillRemote`）

### `reviewSkillAction`

- 原函数定义：`store/heritageSkills.js:109`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminSkills.vue:310`

### `skillLevels`

- 原函数定义：`store/heritageSkills.js:11`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleSkills.vue:385`

### `skillSchools`

- 原函数定义：`store/heritageSkills.js:14`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleSkills.vue:385`

### `skillStatusMap`

- 原函数定义：`store/heritageSkills.js:20`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminSkills.vue:310`
  - 页面 `views/console/ConsoleSkills.vue:385`

### `submitSkillAction`

- 原函数定义：`store/heritageSkills.js:87`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleSkills.vue:385`

### `toggleOfflineSkill`

- 原函数定义：`store/heritageSkills.js:98`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleSkills.vue:385`

### `updateSkillAction`

- 原函数定义：`store/heritageSkills.js:66`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminSkills.vue:310`
  - 页面 `views/console/ConsoleSkills.vue:385`

### `heritageStudents`

- 原函数定义：`store/heritageStudents.js:8`
- 被 4 个页面文件调用，共 5 处导入：
  - 模块 `store/heritageInventory.js:3`
  - 页面 `views/admin/AdminOverview.vue:54`
  - 页面 `views/console/ConsoleLayout.vue:83`
  - 页面 `views/console/ConsoleOverview.vue:147`
  - 页面 `views/console/ConsoleStudents.vue:231`

### `loadStudents`

- 原函数定义：`store/heritageStudents.js:46`
- 被 4 个页面文件调用，共 4 处导入：
  - 页面 `views/admin/AdminOrders.vue:358`
  - 页面 `views/admin/AdminOverview.vue:54`
  - 页面 `views/console/ConsoleOverview.vue:147`
  - 页面 `views/console/ConsoleStudents.vue:231`

### `markStudentDoneAction`

- 原函数定义：`store/heritageStudents.js:99`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminStudents.vue:103`
  - 页面 `views/console/ConsoleStudents.vue:231`

### `saveStudentMaterialPlan`

- 原函数定义：`store/heritageStudents.js:88`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleStudents.vue:231`

### `studentStatusMap`

- 原函数定义：`store/heritageStudents.js:11`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminStudents.vue:103`
  - 页面 `views/console/ConsoleStudents.vue:231`

### `updateStudentAction`

- 原函数定义：`store/heritageStudents.js:67`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleStudents.vue:231`

### `addLog`

- 原函数定义：`store/heritageSystem.js:137`
- 被 17 个页面文件调用，共 17 处导入：
  - 页面 `views/admin/AdminAccounts.vue:146`
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/admin/AdminCourses.vue:224`
  - 页面 `views/admin/AdminInheritors.vue:165`
  - 页面 `views/admin/AdminMessages.vue:94`
  - 页面 `views/admin/AdminOrders.vue:358`
  - 页面 `views/admin/AdminProductReview.vue:214`
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/admin/AdminSkills.vue:310`
  - 页面 `views/admin/AdminStudents.vue:103`
  - 页面 `views/admin/AdminTraining.vue:139`
  - 页面 `views/admin/AdminVideos.vue:168`
  - 页面 `views/console/ConsoleCourseEdit.vue:270`
  - 页面 `views/console/ConsoleInventory.vue:177`
  - 页面 `views/console/ConsoleProfile.vue:152`
  - 页面 `views/console/ConsoleStudents.vue:231`
  - 页面 `views/console/ConsoleTraining.vue:172`

### `brandGlyph`

- 原函数定义：`store/heritageSystem.js:21`
- 被 5 个页面文件调用，共 5 处导入：
  - 页面 `views/admin/AdminLayout.vue:77`
  - 页面 `views/auth/Login.vue:90`
  - 页面 `views/auth/Register.vue:145`
  - 页面 `views/console/ConsoleLayout.vue:83`
  - 页面 `views/user/common/nav.vue:36`

### `brandLogo`

- 原函数定义：`store/heritageSystem.js:20`
- 被 5 个页面文件调用，共 5 处导入：
  - 页面 `views/admin/AdminLayout.vue:77`
  - 页面 `views/auth/Login.vue:90`
  - 页面 `views/auth/Register.vue:145`
  - 页面 `views/console/ConsoleLayout.vue:83`
  - 页面 `views/user/common/nav.vue:36`

### `brandShort`

- 原函数定义：`store/heritageSystem.js:22`
- 被 5 个页面文件调用，共 5 处导入：
  - 页面 `views/admin/AdminLayout.vue:77`
  - 页面 `views/auth/Login.vue:90`
  - 页面 `views/auth/Register.vue:145`
  - 页面 `views/console/ConsoleLayout.vue:83`
  - 页面 `views/user/common/nav.vue:36`

### `checkUploadFile`

- 原函数定义：`store/heritageSystem.js:63`
- 被 8 个页面文件调用，共 8 处导入：
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/admin/AdminInheritors.vue:165`
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/console/ConsoleCourseEdit.vue:270`
  - 页面 `views/console/ConsoleProfile.vue:152`
  - 页面 `views/console/ConsoleSkills.vue:385`
  - 页面 `views/console/ConsoleWorks.vue:192`
  - 页面 `views/user/profile/Profile.vue:148`

### `clearSystemLogo`

- 原函数定义：`store/heritageSystem.js:201`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminConfig.vue:182`

### `homeConfig`

- 原函数定义：`store/heritageSystem.js:102`
- 被 4 个页面文件调用，共 4 处导入：
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/user/course/CourseList.vue:168`
  - 页面 `views/user/home/Home.vue:111`
  - 页面 `views/user/product/ProductList.vue:188`

### `loadConfig`

- 原函数定义：`store/heritageSystem.js:173`
- 被 4 个页面文件调用，共 5 处导入：
  - 模块 `main.js:9`
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/user/course/CourseList.vue:168`
  - 页面 `views/user/home/Home.vue:111`
  - 页面 `views/user/product/ProductList.vue:188`

### `logTypeMap`

- 原函数定义：`store/heritageSystem.js:110`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminLogs.vue:60`

### `saveConfigRemote`

- 原函数定义：`store/heritageSystem.js:209`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminConfig.vue:182`

### `systemConfig`

- 原函数定义：`store/heritageSystem.js:7`
- 被 2 个页面文件调用，共 3 处导入：
  - 模块 `main.js:9`
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/user/common/foot.vue:32`

### `uploadLimitCount`

- 原函数定义：`store/heritageSystem.js:40`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/console/ConsoleWorks.vue:192`

### `uploadLimitMb`

- 原函数定义：`store/heritageSystem.js:32`
- 被 5 个页面文件调用，共 5 处导入：
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/console/ConsoleCourseEdit.vue:270`
  - 页面 `views/console/ConsoleProfile.vue:152`
  - 页面 `views/console/ConsoleSkills.vue:385`
  - 页面 `views/console/ConsoleWorks.vue:192`

### `uploadSystemLogo`

- 原函数定义：`store/heritageSystem.js:192`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/admin/AdminConfig.vue:182`

### `videoUploadAllowed`

- 原函数定义：`store/heritageSystem.js:45`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/console/ConsoleCourseEdit.vue:270`

### `addTrainingRecord`

- 原函数定义：`store/heritageTrainingRecords.js:50`
- 被 3 个页面文件调用，共 3 处导入：
  - 页面 `views/admin/AdminTraining.vue:139`
  - 页面 `views/console/ConsoleStudents.vue:231`
  - 页面 `views/console/ConsoleTraining.vue:172`

### `loadTrainingRecords`

- 原函数定义：`store/heritageTrainingRecords.js:40`
- 被 3 个页面文件调用，共 3 处导入：
  - 页面 `views/console/ConsoleOverview.vue:147`
  - 页面 `views/console/ConsoleStudents.vue:231`
  - 页面 `views/console/ConsoleTraining.vue:172`

### `removeTrainingRecord`

- 原函数定义：`store/heritageTrainingRecords.js:72`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminTraining.vue:139`
  - 页面 `views/console/ConsoleTraining.vue:172`

### `trainingRecords`

- 原函数定义：`store/heritageTrainingRecords.js:13`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/console/ConsoleOverview.vue:147`
  - 页面 `views/console/ConsoleTraining.vue:172`

### `updateTrainingRecordAction`

- 原函数定义：`store/heritageTrainingRecords.js:61`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/admin/AdminTraining.vue:139`
  - 页面 `views/console/ConsoleTraining.vue:172`

### `addEnrollment`

- 原函数定义：`store/index.js:124`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/Pay.vue:77`

### `addOrder`

- 原函数定义：`store/index.js:240`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/Pay.vue:77`

### `addProductOrder`

- 原函数定义：`store/index.js:287`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/product/ProductDetail.vue:201`

### `authState`

- 原函数定义：`store/index.js:374`
- 被 29 个页面文件调用，共 30 处导入：
  - 模块 `router/index.js:55`
  - 页面 `views/admin/AdminAccounts.vue:146`
  - 页面 `views/admin/AdminConfig.vue:182`
  - 页面 `views/admin/AdminCourses.vue:224`
  - 页面 `views/admin/AdminInheritors.vue:165`
  - 页面 `views/admin/AdminLayout.vue:77`
  - 页面 `views/admin/AdminMessages.vue:94`
  - 页面 `views/admin/AdminOrders.vue:358`
  - 页面 `views/admin/AdminOverview.vue:54`
  - 页面 `views/admin/AdminProductReview.vue:214`
  - 页面 `views/admin/AdminProducts.vue:399`
  - 页面 `views/admin/AdminSkills.vue:310`
  - 页面 `views/admin/AdminStudents.vue:103`
  - 页面 `views/admin/AdminTraining.vue:139`
  - 页面 `views/admin/AdminVideos.vue:168`
  - 页面 `views/auth/Login.vue:90`
  - 页面 `views/console/ConsoleCourseEdit.vue:270`
  - 页面 `views/console/ConsoleInventory.vue:177`
  - 页面 `views/console/ConsoleLayout.vue:83`
  - 页面 `views/console/ConsoleOverview.vue:147`
  - 页面 `views/console/ConsoleProfile.vue:152`
  - 页面 `views/console/ConsoleStudents.vue:231`
  - 页面 `views/console/ConsoleTraining.vue:172`
  - 页面 `views/console/ConsoleWorks.vue:192`
  - 页面 `views/user/about/Contact.vue:87`
  - 页面 `views/user/common/nav.vue:36`
  - 页面 `views/user/course/CourseDetail.vue:139`
  - 页面 `views/user/product/ProductDetail.vue:201`
  - 页面 `views/user/profile/Pay.vue:77`
  - 页面 `views/user/profile/Profile.vue:148`

### `cancelMyOrder`

- 原函数定义：`store/index.js:345`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/MyOrder.vue:128`

### `confirmMyOrder`

- 原函数定义：`store/index.js:335`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/MyOrder.vue:128`

### `enrollmentOf`

- 原函数定义：`store/index.js:174`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/user/course/CourseDetail.vue:139`
  - 页面 `views/user/profile/Pay.vue:77`

### `enrollmentState`

- 原函数定义：`store/index.js:91`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/user/profile/MyEnroll.vue:97`
  - 页面 `views/user/profile/MyLearn.vue:119`

### `favoriteState`

- 原函数定义：`store/index.js:40`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/MyFavorite.vue:62`

### `homeOf`

- 原函数定义：`store/index.js:418`
- 被 2 个页面文件调用，共 3 处导入：
  - 模块 `router/index.js:55`
  - 页面 `views/user/course/CourseDetail.vue:139`
  - 页面 `views/user/profile/Pay.vue:77`

### `isEnrolled`

- 原函数定义：`store/index.js:180`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/user/course/CourseDetail.vue:139`
  - 页面 `views/user/profile/Pay.vue:77`

### `isFavorite`

- 原函数定义：`store/index.js:54`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/product/ProductDetail.vue:201`

### `isLoggedIn`

- 原函数定义：`store/index.js:412`
- 被 7 个页面文件调用，共 10 处导入：
  - 模块 `main.js:9`
  - 模块 `router/index.js:55`
  - 模块 `store/heritageProfile.js:5`
  - 页面 `views/auth/Login.vue:90`
  - 页面 `views/user/common/nav.vue:36`
  - 页面 `views/user/course/CourseDetail.vue:139`
  - 页面 `views/user/product/ProductDetail.vue:201`
  - 页面 `views/user/profile/Pay.vue:77`
  - 页面 `views/user/profile/Profile.vue:148`
  - 页面 `views/user/profile/ProfileAside.vue:56`

### `loadEnrollments`

- 原函数定义：`store/index.js:95`
- 被 3 个页面文件调用，共 3 处导入：
  - 页面 `views/user/course/CourseDetail.vue:139`
  - 页面 `views/user/profile/MyEnroll.vue:97`
  - 页面 `views/user/profile/MyLearn.vue:119`

### `loadFavorites`

- 原函数定义：`store/index.js:44`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/user/product/ProductDetail.vue:201`
  - 页面 `views/user/profile/MyFavorite.vue:62`

### `loadOrders`

- 原函数定义：`store/index.js:208`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/MyOrder.vue:128`

### `loadUserData`

- 原函数定义：`store/index.js:380`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `main.js:9`

### `login`

- 原函数定义：`store/index.js:388`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/auth/Login.vue:90`

### `logout`

- 原函数定义：`store/index.js:402`
- 被 4 个页面文件调用，共 4 处导入：
  - 页面 `views/admin/AdminLayout.vue:77`（本地名 `doLogout`）
  - 页面 `views/console/ConsoleLayout.vue:83`（本地名 `doLogout`）
  - 页面 `views/user/common/nav.vue:36`
  - 页面 `views/user/profile/ProfileAside.vue:56`

### `orderState`

- 原函数定义：`store/index.js:204`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/MyOrder.vue:128`

### `payMyOrder`

- 原函数定义：`store/index.js:317`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/MyOrder.vue:128`

### `resolveLanding`

- 原函数定义：`store/index.js:426`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/auth/Login.vue:90`

### `toggleFavorite`

- 原函数定义：`store/index.js:69`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/product/ProductDetail.vue:201`

### `unfavoriteProduct`

- 原函数定义：`store/index.js:60`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/MyFavorite.vue:62`

### `updateMyEnrollmentCompleted`

- 原函数定义：`store/index.js:187`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/MyLearn.vue:119`

### `addAddress`

- 原函数定义：`store/userAddresses.js:55`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/user/product/ProductDetail.vue:201`
  - 页面 `views/user/profile/MyAddress.vue:84`

### `addresses`

- 原函数定义：`store/userAddresses.js:8`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/user/product/ProductDetail.vue:201`（本地名 `bookAddresses`）
  - 页面 `views/user/profile/MyAddress.vue:84`

### `loadAddresses`

- 原函数定义：`store/userAddresses.js:44`
- 被 2 个页面文件调用，共 2 处导入：
  - 页面 `views/user/product/ProductDetail.vue:201`
  - 页面 `views/user/profile/MyAddress.vue:84`

### `removeAddress`

- 原函数定义：`store/userAddresses.js:79`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/MyAddress.vue:84`（本地名 `removeAddressRemote`）

### `updateAddressAction`

- 原函数定义：`store/userAddresses.js:66`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/MyAddress.vue:84`

## 路由（router/）

### `default`

- 原函数定义：`router/index.js:91`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `main.js:8`（本地名 `router`）

## 组合函数（composables/）

### `usePagedList`

- 原函数定义：`composables/usePagedList.js:7`
- 被 11 个页面文件调用，共 11 处导入：
  - 页面 `views/admin/AdminAccounts.vue:157`
  - 页面 `views/admin/AdminCourses.vue:225`
  - 页面 `views/admin/AdminInheritors.vue:177`
  - 页面 `views/admin/AdminLogs.vue:61`
  - 页面 `views/admin/AdminMessages.vue:101`
  - 页面 `views/admin/AdminOrders.vue:379`
  - 页面 `views/admin/AdminProductReview.vue:215`
  - 页面 `views/admin/AdminSkills.vue:315`
  - 页面 `views/admin/AdminStudents.vue:104`
  - 页面 `views/admin/AdminTraining.vue:148`
  - 页面 `views/admin/AdminVideos.vue:169`

## 组件（.vue）

### `default`

- 原函数定义：`App.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `main.js:7`（本地名 `App`）

### `default`

- 原函数定义：`views/admin/AdminAccounts.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:48`（本地名 `AdminAccounts`）

### `default`

- 原函数定义：`views/admin/AdminConfig.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:49`（本地名 `AdminConfig`）

### `default`

- 原函数定义：`views/admin/AdminCourses.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:39`（本地名 `AdminCourses`）

### `default`

- 原函数定义：`views/admin/AdminInheritors.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:46`（本地名 `AdminInheritors`）

### `default`

- 原函数定义：`views/admin/AdminLayout.vue:1`
- 被 14 个页面文件调用，共 14 处导入：
  - 页面 `views/admin/AdminAccounts.vue:143`（本地名 `AdminLayout`）
  - 页面 `views/admin/AdminConfig.vue:180`（本地名 `AdminLayout`）
  - 页面 `views/admin/AdminCourses.vue:221`（本地名 `AdminLayout`）
  - 页面 `views/admin/AdminInheritors.vue:163`（本地名 `AdminLayout`）
  - 页面 `views/admin/AdminLogs.vue:58`（本地名 `AdminLayout`）
  - 页面 `views/admin/AdminMessages.vue:93`（本地名 `AdminLayout`）
  - 页面 `views/admin/AdminOrders.vue:354`（本地名 `AdminLayout`）
  - 页面 `views/admin/AdminOverview.vue:53`（本地名 `AdminLayout`）
  - 页面 `views/admin/AdminProductReview.vue:211`（本地名 `AdminLayout`）
  - 页面 `views/admin/AdminProducts.vue:393`（本地名 `AdminLayout`）
  - 页面 `views/admin/AdminSkills.vue:306`（本地名 `AdminLayout`）
  - 页面 `views/admin/AdminStudents.vue:100`（本地名 `AdminLayout`）
  - 页面 `views/admin/AdminTraining.vue:138`（本地名 `AdminLayout`）
  - 页面 `views/admin/AdminVideos.vue:165`（本地名 `AdminLayout`）

### `default`

- 原函数定义：`views/admin/AdminLogs.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:50`（本地名 `AdminLogs`）

### `default`

- 原函数定义：`views/admin/AdminMessages.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:51`（本地名 `AdminMessages`）

### `default`

- 原函数定义：`views/admin/AdminOrders.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:43`（本地名 `AdminOrders`）

### `default`

- 原函数定义：`views/admin/AdminOverview.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:38`（本地名 `AdminOverview`）

### `default`

- 原函数定义：`views/admin/AdminProductReview.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:42`（本地名 `AdminProductReview`）

### `default`

- 原函数定义：`views/admin/AdminProducts.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:47`（本地名 `AdminProducts`）

### `default`

- 原函数定义：`views/admin/AdminSkills.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:41`（本地名 `AdminSkills`）

### `default`

- 原函数定义：`views/admin/AdminStudents.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:44`（本地名 `AdminStudents`）

### `default`

- 原函数定义：`views/admin/AdminTraining.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:45`（本地名 `AdminTraining`）

### `default`

- 原函数定义：`views/admin/AdminVideos.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:40`（本地名 `AdminVideos`）

### `default`

- 原函数定义：`views/auth/Login.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:53`（本地名 `Login`）

### `default`

- 原函数定义：`views/auth/Register.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:54`（本地名 `Register`）

### `default`

- 原函数定义：`views/console/ConsoleCourseEdit.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:29`（本地名 `ConsoleCourseEdit`）

### `default`

- 原函数定义：`views/console/ConsoleCourses.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:28`（本地名 `ConsoleCourses`）

### `default`

- 原函数定义：`views/console/ConsoleInventory.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:31`（本地名 `ConsoleInventory`）

### `default`

- 原函数定义：`views/console/ConsoleLayout.vue:1`
- 被 9 个页面文件调用，共 9 处导入：
  - 页面 `views/console/ConsoleCourseEdit.vue:267`（本地名 `ConsoleLayout`）
  - 页面 `views/console/ConsoleCourses.vue:83`（本地名 `ConsoleLayout`）
  - 页面 `views/console/ConsoleInventory.vue:176`（本地名 `ConsoleLayout`）
  - 页面 `views/console/ConsoleOverview.vue:146`（本地名 `ConsoleLayout`）
  - 页面 `views/console/ConsoleProfile.vue:150`（本地名 `ConsoleLayout`）
  - 页面 `views/console/ConsoleSkills.vue:382`（本地名 `ConsoleLayout`）
  - 页面 `views/console/ConsoleStudents.vue:230`（本地名 `ConsoleLayout`）
  - 页面 `views/console/ConsoleTraining.vue:171`（本地名 `ConsoleLayout`）
  - 页面 `views/console/ConsoleWorks.vue:191`（本地名 `ConsoleLayout`）

### `default`

- 原函数定义：`views/console/ConsoleOverview.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:27`（本地名 `ConsoleOverview`）

### `default`

- 原函数定义：`views/console/ConsoleProfile.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:35`（本地名 `ConsoleProfile`）

### `default`

- 原函数定义：`views/console/ConsoleSkills.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:32`（本地名 `ConsoleSkills`）

### `default`

- 原函数定义：`views/console/ConsoleStudents.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:33`（本地名 `ConsoleStudents`）

### `default`

- 原函数定义：`views/console/ConsoleTraining.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:34`（本地名 `ConsoleTraining`）

### `default`

- 原函数定义：`views/console/ConsoleWorks.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:30`（本地名 `ConsoleWorks`）

### `default`

- 原函数定义：`views/user/about/About.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:22`（本地名 `About`）

### `default`

- 原函数定义：`views/user/about/Agreement.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:24`（本地名 `Agreement`）

### `default`

- 原函数定义：`views/user/about/Contact.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:23`（本地名 `Contact`）

### `default`

- 原函数定义：`views/user/archive/ArchiveDetail.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:8`（本地名 `ArchiveDetail`）

### `default`

- 原函数定义：`views/user/archive/ArchiveList.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:7`（本地名 `ArchiveList`）

### `default`

- 原函数定义：`views/user/archive/SkillDetailPage.vue:1`
- 被 3 个页面文件调用，共 3 处导入：
  - 页面 `views/admin/AdminSkills.vue:307`（本地名 `SkillDetailPage`）
  - 页面 `views/console/ConsoleSkills.vue:383`（本地名 `SkillDetailPage`）
  - 页面 `views/user/archive/ArchiveDetail.vue:17`（本地名 `SkillDetailPage`）

### `default`

- 原函数定义：`views/user/common/foot.vue:35`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `App.vue:21`（本地名 `Foot`）

### `default`

- 原函数定义：`views/user/common/nav.vue:40`
- 被 19 个页面文件调用，共 19 处导入：
  - 页面 `views/user/about/About.vue:99`（本地名 `Nav`）
  - 页面 `views/user/about/Agreement.vue:42`（本地名 `Nav`）
  - 页面 `views/user/about/Contact.vue:86`（本地名 `Nav`）
  - 页面 `views/user/archive/ArchiveDetail.vue:16`（本地名 `Nav`）
  - 页面 `views/user/archive/ArchiveList.vue:101`（本地名 `Nav`）
  - 页面 `views/user/course/CourseDetail.vue:138`（本地名 `Nav`）
  - 页面 `views/user/course/CourseList.vue:167`（本地名 `Nav`）
  - 页面 `views/user/home/Home.vue:110`（本地名 `Nav`）
  - 页面 `views/user/inheritor/InheritorDetail.vue:145`（本地名 `Nav`）
  - 页面 `views/user/inheritor/InheritorShow.vue:86`（本地名 `Nav`）
  - 页面 `views/user/product/ProductDetail.vue:200`（本地名 `Nav`）
  - 页面 `views/user/product/ProductList.vue:187`（本地名 `Nav`）
  - 页面 `views/user/profile/MyAddress.vue:82`（本地名 `Nav`）
  - 页面 `views/user/profile/MyEnroll.vue:95`（本地名 `Nav`）
  - 页面 `views/user/profile/MyFavorite.vue:60`（本地名 `Nav`）
  - 页面 `views/user/profile/MyLearn.vue:118`（本地名 `Nav`）
  - 页面 `views/user/profile/MyOrder.vue:126`（本地名 `Nav`）
  - 页面 `views/user/profile/Pay.vue:76`（本地名 `Nav`）
  - 页面 `views/user/profile/Profile.vue:146`（本地名 `Nav`）

### `default`

- 原函数定义：`views/user/course/CourseDetail.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:10`（本地名 `CourseDetail`）

### `default`

- 原函数定义：`views/user/course/CourseList.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:9`（本地名 `CourseList`）

### `default`

- 原函数定义：`views/user/home/Home.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:6`（本地名 `HomeView`）

### `default`

- 原函数定义：`views/user/inheritor/InheritorDetail.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:14`（本地名 `InheritorDetail`）

### `default`

- 原函数定义：`views/user/inheritor/InheritorShow.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:13`（本地名 `InheritorShow`）

### `default`

- 原函数定义：`views/user/product/ProductDetail.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:12`（本地名 `ProductDetail`）

### `default`

- 原函数定义：`views/user/product/ProductList.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:11`（本地名 `ProductList`）

### `default`

- 原函数定义：`views/user/profile/MyAddress.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:19`（本地名 `MyAddress`）

### `default`

- 原函数定义：`views/user/profile/MyEnroll.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:16`（本地名 `MyEnroll`）

### `default`

- 原函数定义：`views/user/profile/MyFavorite.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:18`（本地名 `MyFavorite`）

### `default`

- 原函数定义：`views/user/profile/MyLearn.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:21`（本地名 `MyLearn`）

### `default`

- 原函数定义：`views/user/profile/MyOrder.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:17`（本地名 `MyOrder`）

### `default`

- 原函数定义：`views/user/profile/Pay.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:20`（本地名 `Pay`）

### `default`

- 原函数定义：`views/user/profile/Profile.vue:1`
- 被 0 个页面文件调用，共 1 处导入：
  - 模块 `router/index.js:15`（本地名 `Profile`）

### `default`

- 原函数定义：`views/user/profile/ProfileAside.vue:1`
- 被 5 个页面文件调用，共 5 处导入：
  - 页面 `views/user/profile/MyAddress.vue:83`（本地名 `ProfileAside`）
  - 页面 `views/user/profile/MyEnroll.vue:96`（本地名 `ProfileAside`）
  - 页面 `views/user/profile/MyFavorite.vue:61`（本地名 `ProfileAside`）
  - 页面 `views/user/profile/MyOrder.vue:127`（本地名 `ProfileAside`）
  - 页面 `views/user/profile/Profile.vue:147`（本地名 `ProfileAside`）

## 其他

### `chinaRegions`

- 原函数定义：`assets/china-regions.js:4`
- 被 1 个页面文件调用，共 1 处导入：
  - 页面 `views/user/profile/Profile.vue:150`
