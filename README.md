# Trium

是为《智能机电系统实践》课程项目，目的在于实现一个能对物品进行识别、抓取、运输、卸载的机器人。该课程又名机械制图实践，在计算设计之外强调实际制造。因此，应用可行性（及应用效率）而非理论可行性是本项目更加关注之处。

> [!NOTE]
> 本仓库主要存储算法代码，同时也存储一部分其他材料。

## Getting Started

- 新的代码请在[`src`](src/)创建新文件夹并放入。
- 代码要用到的数据请在[`assets`](assets/)创建新文件夹并放入，零碎的数据可放入[`assets/miscellaneous`](assets/miscellaneous/)。（**加工数据时，请不要删除旧的数据，而是创建一个新文件夹并将加工后的数据放入**）
- 文档类材料请放入[`doc`](doc/)。当系统设计发生增添或删减时，请及时更新文档。如果有值得额外说明的问题，可以在其中增加新文件加以注释。

> [!TIP]
> 若是深陷迷茫，不妨运行[`Trium_Intro`](Trium_Intro.bat)。

## About This Repository

### File Structure

- [`assets`](assets/) -- 一些图片，以及会在算法中用到的非代码数据。
- [`doc`](doc/) -- 一些其他材料，如设计方案等。
- [`src`](src/) -- 源代码。
  <!-- - [`simulation`](src/simulation/) -- 基于pymunk的路径规划与避障算法。
  - [`simulation2`](src/simulation2/) -- 基于pymunk的路径规划与避障算法第二代。真实性++，收集效果--
  - [`vision`](src/vision/) -- 基于树莓派OpenCV的图像识别算法。
  - [vision3/](src/vision3/) -- 基于树莓派OpenCV的图像识别算法第三代。
  - [vision2/](src/vision2/) -- 基于树莓派OpenCV的图像识别算法第二代（但是比第三代更新，编号问题）。
  - [main_prog](src/main_prog) -- STM32主程序。由于STM32工程的代码相对较为繁杂，此处存放的又为完整工程文件，因此CubeIDE端的同步请手动进行操作。在CubeIDE中进行更改后，请将完整工程文件夹拷贝至此处替换。 -->
  - [`algorithm`](src/algorithm/) -- 一些算法，部署于树莓派4B。
  - [`communication`](src/communication/) -- 通信相关的代码，如串口、摄像头等。
  - [`archive`](src/archive/) -- 代码存档，包括有趣的尝试和备份代码。关于STM32部分的代码请参考[`README.md`](src/archive/main_prog/README.md)。

### Documentation Norm

A typical pythonic documentation should behave like this:

```python
def func(arg1: int, arg2: str) -> bool:
    """
    Here is the function's brief introduction.

    - You may add some detailed description here.

    Args:
        arg1 (int): Description of the first argument.
        arg2 (str): Description of the second argument.

    Returns:
        value (bool): Always True.

    Note:
        Some additional notes may be placed here, such as problems to be solved, etc.
    """
    value = True
    return value
```

This documentation style guide is based on [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html). It is a simplified version, and thus the `example` part is omitted since we are not writing a complicated project.

### Git Norm

A commit message should be clear and concise in order that problem dealing can be more efficient. It ought to be in the following format:

```git
<type>(<scoop>): <subject>
// <BLANK LINE>
<body>
// <BLANK LINE>
<footer>
```

- `<type>`: The type of the commit, such as `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, etc.
- `<scoop>` (optional) : The scope of the commit, such as `algorithm`, `communication`, `archive`, etc.
- `<subject>`: A brief summary of the commit. It should be in the imperative mood without `dot (.)` at the end of a line.
- `<body>` (optional) : A detailed description of the commit.
- `<footer>` (optional) : A footer for the commit, such as `BREAKING CHANGE`, `ISSUES CLOSED`, etc.

> [!NOTE]
> Although pull requests are different from commits, you may follow the same format when writing a pull request.

## Mnky

> [!WARNING]
> 禁止[`†升天†`](https://www.bilibili.com/video/BV1gU4y187xA/)

![Mnky](assets/miscellaneous/justice.jpg)
